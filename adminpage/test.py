from django.test import TestCase ,Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from . import views as views
# import requests
import json

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
        User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu',password='1234')
        resp = c.get('/api/a/activity/list')
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # return empty list
        self.assertEqual(mess['data'],[])

