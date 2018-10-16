import json
import logging
import time
import datetime

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

 
from codex.baseerror import *
from codex.baseview import APIView
from WeChatTicket.settings import MEDIA_ROOT,SITE_DOMAIN

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
                return
        else:
            raise ValidateError("admin validate error")


class AdminLogout(APIView):

    def get(self):
        pass

    def post(self):
        logout(self.request)


class ActivityList(APIView):

    def get(self):
        if self.request.user.is_authenticated():
            # to do status>=0
            act = Activity.objects.all()
            res = []
            for item in act:
                res.append({
                    'id': item.id,
                    'name': item.name,
                    'description':item.description,
                    'startTime':int(time.mktime(item.start_time.timetuple())),
                    'endTime':int(time.mktime(item.end_time.timetuple())),
                    'place':item.place,
                    'bookStart':int(time.mktime(item.book_start.timetuple())),
                    'bookEnd':int(time.mktime(item.book_end.timetuple())),
                    'currentTime':int(time.time()),
                    'status':item.status
                    })
            return res
        else:
            raise LoginError('')
    def post(self):
        pass

# to do lock
class ActivityDelete(APIView):

    def get(self):
        pass

    def post(self):
        # to do delete pic
        self.check_input('id')
        try:
            act = Activity.objects.filter(id=self.input['id'])
            for item in act:
                item.delete()
        except :
            raise LogicError('delete fail')


# to do
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

# to do check if local can be used or not 
class ImageUpload(APIView):

    def get(self):
        pass

    def post(self):
        if self.request.user.is_authenticated():
            img = self.input['image']
            path = default_storage.save(MEDIA_ROOT+'/uploads/'+img[0].name,ContentFile(img[0].read()))
            return 'http://'+SITE_DOMAIN+'/uploads/'+img[0].name
        else:
            raise LoginError('')

class ActivityDetail(APIView):
    def getTime(self, item):
        return int(time.mktime(item.timetuple()))

    def get(self):
        if self.request.user.is_authenticated():
            item = Activity.objects.get(pk=self.input['id'])
            used_tickets = item.total_tickets-item.remain_tickets
            return {
                    'name': item.name,
                    'key' : item.key,
                    'description':item.description,
                    'startTime':int(time.mktime(item.start_time.timetuple())),
                    'endTime':int(time.mktime(item.end_time.timetuple())),
                    'place':item.place,
                    'bookStart':int(time.mktime(item.book_start.timetuple())),
                    'bookEnd':int(time.mktime(item.book_end.timetuple())),
                    'totalTickets': item.total_tickets,
                    'usedTickets': used_tickets,
                    'currentTime':int(time.time()),
                    'status':item.status
                }
        else:
            raise LoginError('')

    def post(self):
        if self.request.user.is_authenticated():
            item = Activity.objects.get(pk=self.input['id'])
            # to do lock
            # if publish can't be modefied
            item.name = self.input['name']
            item.description = self.input['description']
            item.start_time = self.input['startTime']
            item.end_time = self.input['endTime']
            item.book_start = self.input['bookStart']
            item.book_end = self.input['bookEnd']
            item.place = self.input['place']
            item.total_tickets = self.input['totalTickets']
            item.pic_url = self.input['picUrl']
            item.status = self.input['status']
            item.save()
            pass
        else:
            raise LoginError('')

def testDemoAdd(x, y):
    return x + y