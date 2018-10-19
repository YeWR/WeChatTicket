import time
import os

from django.contrib.auth import authenticate, logout, login
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

from codex.baseerror import *
from codex.baseview import APIView
from WeChatTicket.settings import SITE_DOMAIN, MEDIA_ROOT
from wechat.views import CustomWeChatView
from wechat.models import Activity, Ticket


class AdminLogin(APIView):

    def get(self):
        if self.request.user.is_authenticated():
            return
        else:
            raise LoginError('')

    def post(self):
        self.check_input('username', 'password')
        user = authenticate(username=self.input['username'], password=self.input['password'])
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
                if item.status >= 0:
                    res.append({
                        'id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'startTime': self.getTimeStamp(item.start_time),
                        'endTime': self.getTimeStamp(item.end_time),
                        'place': item.place,
                        'bookStart': self.getTimeStamp(item.book_start),
                        'bookEnd': self.getTimeStamp(item.book_end),
                        'currentTime': int(time.time()),
                        'status': item.status
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
        if self.request.user.is_authenticated():
            self.check_input('id')
            try:
                with transaction.atomic():
                    act = Activity.objects.select_for_update().filter(id=self.input['id'])
                    for item in act:
                        item.status = Activity.STATUS_DELETED
                        item.save()
            except:
                raise LogicError('delete fail')
        else:
            raise LoginError('')


class ActivityCreate(APIView):

    def get(self):
        pass

    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart',
                             'bookEnd', 'totalTickets', 'status')
            check = Activity.objects.filter(name=self.input['name'],start_time=self.input['startTime']).first()
            if check is not None:
                raise LogicError('already have this activity')
            if len(self.input['picUrl']) > 256:
                raise LogicError('picUrl is too long, please upload local picture')
            act = Activity(name=self.input['name'], key=self.input['key'], place=self.input['place'],
                           description=self.input['description'], pic_url=self.input['picUrl'],
                           start_time=self.input['startTime'],
                           end_time=self.input['endTime'], book_start=self.input['bookStart'],
                           book_end=self.input['bookEnd'],
                           total_tickets=self.input['totalTickets'], status=self.input['status'],
                           remain_tickets=self.input['totalTickets'])
            act.save()
            return act.id
        else:
            raise LoginError('')


class ImageUpload(APIView):

    def get(self):
        pass

    def post(self):
        if self.request.user.is_authenticated():
            img = self.input['image']
            path = default_storage.save(MEDIA_ROOT + '/' + img[0].name, ContentFile(img[0].read()))
            names = path.split('/')
            name_final = names[len(names) - 1]
            return 'http://' + SITE_DOMAIN + '/uploads/' + name_final
        else:
            raise LoginError('')


class ActivityDetail(APIView):
    def getTimeStamp(self, str_time):
        return int(time.mktime(str_time.timetuple()))

    def isFirstEarly(self, str_time1, str_time2):
        if (str_time1 - str_time2 > 0):
            return 0
        else:
            return 1

    def get(self):
        if self.request.user.is_authenticated():
            self.check_input('id')
            item = Activity.objects.filter(pk=self.input['id']).first()
            used_tickets = item.total_tickets - item.remain_tickets
            return {
                'name': item.name,
                'key': item.key,
                'description': item.description,
                'startTime': self.getTimeStamp(item.start_time),
                'endTime': self.getTimeStamp(item.end_time),
                'place': item.place,
                'bookStart': self.getTimeStamp(item.book_start),
                'bookEnd': self.getTimeStamp(item.book_end),
                'totalTickets': item.total_tickets,
                'usedTickets': used_tickets,
                'currentTime': int(time.time()),
                'status': item.status
            }
        else:
            raise LoginError('')

    def post(self):
        if self.request.user.is_authenticated():
            with transaction.atomic():
                self.check_input('id', 'description', 'status', 'picUrl', 'place', 'name', 'startTime', 'endTime',
                                 'bookStart', 'bookEnd', 'totalTickets')
                item = Activity.objects.select_for_update().filter(id=self.input['id']).first()
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
                    name = names[len(names) - 1]
                    path = os.path.join(MEDIA_ROOT, name)
                    if os.path.isfile(path):
                        os.remove(path)
                    # change data
                    item.pic_url = self.input['picUrl']

                if (item.status) == Activity.STATUS_SAVED:
                    item.book_start = self.input['bookStart']
                    item.name = self.input['name']
                    item.place = self.input['place']

                if self.isFirstEarly(int(time.time()), self.getTimeStamp(end_time)):
                    item.start_time = self.input['startTime']
                    item.end_time = self.input['endTime']

                if self.isFirstEarly(int(time.time()), self.getTimeStamp(start_time)):
                    item.book_end = self.input['bookEnd']

                if self.isFirstEarly(int(time.time()), self.getTimeStamp(book_start)):
                    item.total_tickets = self.input['totalTickets']

                item.save()

        else:
            raise LoginError('')


class ActivityMenu(APIView):

    def get(self):
        if self.request.user.is_authenticated():
            # all acti be published and order by book_end
            items = Activity.objects.filter(status=Activity.STATUS_PUBLISHED).order_by('book_end')
            menu = []
            count = 1
            for item in items:
                menu.append({
                    'id': item.id,
                    'name': item.name,
                    'menuIndex': count
                })
                count += 1
            return menu
        else:
            raise LoginError('')

    def post(self):
        if self.request.user.is_authenticated():
            list = []
            for item in self.input:
                acti = Activity.objects.filter(id=item).first()
                list.append(acti)
            CustomWeChatView.update_menu(list)
            pass
        else:
            raise LoginError('')


class ActivityCheckin(APIView):

    def get(self):
        pass

    def post(self):
        if self.request.user.is_authenticated():
            items = Ticket.objects.filter(activity_id=self.input['actId'])
            try:
                for item in items:
                    if item.student_id == self.input['studentId']:
                        if item.status == Ticket.STATUS_VALID:
                            with transaction.atomic():
                                if item.status == Ticket.STATUS_VALID:
                                    item = Ticket.objects.select_for_update().filter(unique_id=item.unique_id).first()
                                    item.status = Ticket.STATUS_USED
                                    item.save()
                                else:
                                    raise LogicError('')
                            return {
                                'ticket': item.unique_id,
                                'studentId': item.student_id
                            }
            except:
                raise LogicError('检票失败')
            raise LogicError('检票失败')
        else:
            raise LoginError('')
