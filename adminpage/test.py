from django.test import TestCase ,Client
from django.contrib.auth.models import User
from wechat.models import Activity
from django.utils import timezone
from django.contrib.auth import authenticate, logout, login
from . import views as views
# import requests
import json
import logging
import time
import datetime

c = Client(HTTP_USER_AGENT='Mozilla/5.0')
class AuthLoginGet(TestCase):
    def test_admin_login_get(self):
        # c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        resp = c.get('/api/a/login')
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

class AuthLoginPostFail(TestCase):
    def test_admin_login_fail(self):
        # c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        resp = c.post('/api/a/login',{'username':'wu', 'password':'1234'})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 3)
        self.assertEqual(mess['msg'], 'admin validate error')

class AuthLoginPostSucc(TestCase):
    def test_admin_login_success(self):
        # c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        User.objects.create_user(username='wu',email="dui_zhang@163.com",password='1234')
        resp = c.post('/api/a/login',{'username':'wu', 'password':'1234'})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

class AuthLogoutPost(TestCase):
    def test_admin_logout(self):
        resp = c.post('/api/a/logout',{'arg':'useless'})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

class ActiListGetFail(TestCase):
    def test_acti_get_fail(self):
        resp = c.get('/api/a/activity/list')
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

class ActiListGetSucc(TestCase):

    def test_acti_get_succ(self):
        s = Activity(name='11111',key='11',description='aaa',start_time=timezone.now(),\
                     end_time=timezone.now(),place='ss',book_end=timezone.now(),\
                     book_start=timezone.now(),total_tickets='123',status='1',pic_url='sss',remain_tickets='1')
        s.save()
        User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu',password='1234')
        resp = c.get('/api/a/activity/list')
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # return empty list
        self.assertEqual(mess['data'][0]['name'],'11111')

class ActiDeleteSucc(TestCase):

    def test_acti_del_succ(self):
        s = Activity(name='11111',key='11',description='aaa',start_time=timezone.now(),\
                     end_time=timezone.now(),place='ss',book_end=timezone.now(),\
                     book_start=timezone.now(),total_tickets='123',status='1',pic_url='sss',remain_tickets='1')
        s.save()
        name_test = s.name
        resp = c.post('/api/a/activity/delete',{'id': s.id})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        t = Activity.objects.filter(name=name_test)
        self.assertEqual(t[0].status,-1)

class ActiCreateSucc(TestCase):

    def test_acti_create_succ(self):
        tmp = {'name':'111','key':11,'place':'ss','description':'ss','picUrl':'ss',
                                                'startTime':timezone.now(),'endTime':timezone.now(),
                                                'bookStart':timezone.now(),'bookEnd':timezone.now(),
                                                'totalTickets':'aaa','status':'112','remainTickets':'12'}
        resp = c.post('/api/a/activity/create',{'name':'111','key':'11','place':'ss','description':'ss','picUrl':'ss',
                                                'startTime':str(timezone.now()),'endTime':str(timezone.now()),
                                                'bookStart':str(timezone.now()),'bookEnd':str(timezone.now()),
                                                'totalTickets':'123','status':'112'})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        t = Activity.objects.filter(pk=mess['data'])
        self.assertEqual(t[0].name,tmp['name'])

class ImageUpFail(TestCase):

    def test_image_up_fail(self):
        resp = c.post('/api/a/image/upload/',{'image':'useless'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 4)
        self.assertEqual(mess['msg'], '')

class ActiDetailTest(TestCase):
    def getTimeStamp(self, str_time):
        return int(time.mktime(str_time.timetuple()))

    def test_acti_det_get_succ(self):
        s = Activity(name='11111',key='11',description='aaa',start_time=timezone.now(),\
                     end_time=timezone.now(),place='ss',book_end=timezone.now(),\
                     book_start=timezone.now(),total_tickets='123',status='1',pic_url='sss',remain_tickets='1')
        s.save()
        User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu',password='1234')
        resp = c.get('/api/a/activity/detail',{'id':s.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        self.assertEqual(s.name, mess['data']['name'])
        self.assertEqual(s.key, mess['data']['key'])
        self.assertEqual(s.description, mess['data']['description'])
        self.assertEqual(self.getTimeStamp(s.start_time), mess['data']['startTime'])
        self.assertEqual(self.getTimeStamp(s.end_time), mess['data']['endTime'])
        self.assertEqual(s.place, mess['data']['place'])
        self.assertEqual(self.getTimeStamp(s.book_start), mess['data']['bookStart'])
        self.assertEqual(self.getTimeStamp(s.book_end), mess['data']['bookEnd'])
        self.assertEqual(int(s.total_tickets), mess['data']['totalTickets'])
        self.assertEqual(int(s.status), mess['data']['status'])

    def test_acti_det_mod_succ(self):
        s = Activity(name='11111',key='11',description='aaa',start_time=timezone.now(),\
                     end_time=timezone.now(),place='ss',book_end=timezone.now(),\
                     book_start=timezone.now(),total_tickets='123',status='1',pic_url='sss',remain_tickets='1')
        s.save()
        User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu',password='1234')
        resp = c.post('/api/a/activity/detail',{'id':s.id,\
                                                'name':'11111',\
                                                'place':'aaa',\
                                                'description':'ss',\
                                                'picUrl':'to test',
                                                'startTime':s.start_time,\
                                                'endTime':s.end_time,\
                                                'bookStart':s.book_start,\
                                                'bookEnd':s.book_end,\
                                                'totalTickets':'123',\
                                                'status':'1'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # change
        t = Activity.objects.get(pk=s.id)
        self.assertEqual(t.pic_url, 'to test')
