import json
import logging
import time
import datetime
import os

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

 
from codex.baseerror import *
from codex.baseview import APIView
from WeChatTicket.settings import SITE_DOMAIN,MEDIA_ROOT

from wechat.models import Activity

class AdminLogin(APIView):

    def get(self):
        if self.request.user.is_authenticated():
            return
        else:
            raise LoginError('')

    def post(self):
        self.check_input('username', 'password')
        user = authenticate(username=self.input['username'],password=self.input['password'])
        if user is not None:
            if user.is_active:
                login(self.request, user)
            else:
                raise ValidateError("admin validate error")
        else:
            raise ValidateError("admin validate error")

class AdminLogout(APIView):

    def get(self):
        pass

    def post(self):
            logout(self.request)


class ActivityList(APIView):
    def getTimeStamp(self, str_time):
        return int(time.mktime(str_time.timetuple()))

    def get(self):
        if self.request.user.is_authenticated():
            act = Activity.objects.all()
            res = []
            for item in act:
                if item.status >=0 :
                    res.append({
                        'id': item.id,
                        'name': item.name,
                        'description':item.description,
                        'startTime':self.getTimeStamp(item.start_time),
                        'endTime':self.getTimeStamp(item.end_time),
                        'place':item.place,
                        'bookStart':self.getTimeStamp(item.book_start),
                        'bookEnd':self.getTimeStamp(item.book_end),
                        'currentTime':int(time.time()),
                        'status':item.status
                        })
            return res
        else:
            raise LoginError('')
    def post(self):
        pass

class ActivityDelete(APIView):

    def get(self):
        pass

    def post(self):
        self.check_input('id')
        try:
            with transaction.atomic():
                act = Activity.objects.select_for_update().filter(id=self.input['id'])
                for item in act:
                    # delete pic uploaded
                    names = (item.pic_url.split('/'))
                    name = names[len(names)-1]
                    path = os.path.join(MEDIA_ROOT,name)
                    if os.path.isfile(path):
                        os.remove(path)
                    item.delete()
        except :
            raise LogicError('delete fail')


class ActivityCreate(APIView):

    def get(self):
        pass

    def post(self):
        try:
            act = Activity(name=self.input['name'],key=self.input['key'],place=self.input['place'],\
            description=self.input['description'],pic_url=self.input['picUrl'],start_time=self.input['startTime'],\
            end_time=self.input['endTime'],book_start=self.input['bookStart'],book_end=self.input['bookEnd'],\
            total_tickets=self.input['totalTickets'],status=self.input['status'],\
            remain_tickets=self.input['totalTickets'])
            act.save()
            return act.id
        except :
            raise LogicError('create fail')

class ImageUpload(APIView):

    def get(self):
        pass

    def post(self):
        if self.request.user.is_authenticated():
            img = self.input['image']
            path = default_storage.save(MEDIA_ROOT + '/' + img[0].name,ContentFile(img[0].read()))
            names = path.split('/')
            name_final = names[len(names)-1]
            return 'http://'+SITE_DOMAIN+'/uploads/'+name_final
        else:
            raise LoginError('')

class ActivityDetail(APIView):
    def getTimeStamp(self, str_time):
        return int(time.mktime(str_time.timetuple()))

    def isFirstEarly(self, str_time1, str_time2):
        if(str_time1 - str_time2 > 0):
            return 0
        else:
            return 1

    def get(self):
        if self.request.user.is_authenticated():
            item = Activity.objects.get(pk=self.input['id'])
            used_tickets = item.total_tickets-item.remain_tickets
            return {
                    'name': item.name,
                    'key' : item.key,
                    'description':item.description,
                    'startTime':self.getTimeStamp(item.start_time),
                    'endTime':self.getTimeStamp(item.end_time),
                    'place':item.place,
                    'bookStart':self.getTimeStamp(item.book_start),
                    'bookEnd':self.getTimeStamp(item.book_end),
                    'totalTickets': item.total_tickets,
                    'usedTickets': used_tickets,
                    'currentTime':int(time.time()),
                    'status':item.status
                }
        else:
            raise LoginError('')

    def post(self):
        if self.request.user.is_authenticated():
            with transaction.atomic():
                item = Activity.objects.select_for_update().get(pk=self.input['id'])
                # save to forbidden the type change of item
                start_time = item.start_time
                end_time = item.end_time
                book_start = item.book_start
                book_end = item.book_end
                # update
                item.id = self.input['id']
                item.description = self.input['description']
                item.status = self.input['status']
                
                if item.pic_url != self.input['picUrl'] and len(self.input['picUrl']) != 0:
                    # to do change pic 
                    names = (item.pic_url.split('/'))
                    name = names[len(names)-1]
                    path = os.path.join(MEDIA_ROOT,name)
                    if os.path.isfile(path):
                        os.remove(path)
                    # change data
                    item.pic_url = self.input['picUrl']

                if self.isFirstEarly(int(time.time()), self.getTimeStamp(end_time)):
                    item.start_time = self.input['startTime']
                    item.end_time = self.input['endTime']
                if item.status == 0:
                    item.book_start = self.input['bookStart']
                    item.name = self.input['name']
                    item.place = self.input['place']
                if self.isFirstEarly(int(time.time()), self.getTimeStamp(start_time)):
                    item.book_end = self.input['bookEnd']
                if self.isFirstEarly(int(time.time()), self.getTimeStamp(book_start)):
                    item.total_tickets = self.input['totalTickets']

                item.save()
        else:
            raise LoginError('')
