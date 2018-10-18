from codex.baseerror import *
from codex.baseview import APIView
from django.db import transaction

from wechat.models import User, Activity, Ticket
import re, time


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        if self.input['student_id'] == "":
            raise ValidateError('Student ID Empty')
        if self.input['password'] == "":
            raise ValidateError('Password Empty')
        if not re.match("201[0-9][0-9][0-9][0-9][0-9][0-9][0-9]$",self.input['student_id']):
            raise ValidateError('Invaild Student ID')
        with transaction.atomic():
            user = User.objects.select_for_update().filter(student_id=self.input['student_id']).first()
        if user is not None:
            raise ValidateError('Student ID Binded')
        #raise NotImplementedError('You should implement UserBind.validate_user method')

    def get(self):
        self.check_input('openid')
        studentID = User.get_by_openid(self.input['openid']).student_id
        if studentID is None:
            return ''
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        with transaction.atomic():
            user.student_id = self.input['student_id']
            user.save()

class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        try:
            with transaction.atomic():
                activity = Activity.objects.select_for_update().get(id=self.input['id'])
            if activity.status != Activity.STATUS_PUBLISHED:
                raise InputError('Activity not published')
            else:
                return{
                        'name': activity.name,
                        'key' : activity.key,
                        'description':activity.description,
                        'startTime':int(activity.start_time.timestamp()),
                        'endTime':int(activity.end_time.timestamp()),
                        'place':activity.place,
                        'bookStart':int(activity.book_start.timestamp()),
                        'bookEnd':int(activity.book_end.timestamp()),
                        'totalTickets': activity.total_tickets,
                        'picUrl': activity.pic_url,
                        'remainTickets': activity.remain_tickets,
                        'currentTime':int(time.time())
                }
        except Activity.DoesNotExist:
            raise InputError('Activity not found')

class TicketDetail(APIView):

    def get(self):
        self.check_input('openid', 'ticket')
        user = User.get_by_openid(self.input['openid'])
        try:
            studentID = user.student_id
        except:
            raise ValidateError("User not binded")
        try:
            with transaction.atomic():
                ticket = Ticket.objects.select_for_update().get(student_id=studentID, unique_id=self.input['ticket'])
            return{
                    'activityName': ticket.activity.name,
                    'place' : ticket.activity.place,
                    'activityKey': ticket.activity.key,
                    'uniqueID': ticket.unique_id,
                    'startTime':int(ticket.activity.start_time.timestamp()),
                    'endTime':int(ticket.activity.end_time.timestamp()),
                    'currentTime':int(time.time()),
                    'status': ticket.status
            }
        except Ticket.DoesNotExist:
            raise InputError('Ticket not found')


