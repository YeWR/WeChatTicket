from django.test import TestCase ,Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from . import views as views
# import requests
import json

class AuthLoginGet(TestCase):
    def test_admin_login_get(self):
        c = Client()
        resp = c.get('/api/a/login')
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

class AuthLoginPostFail(TestCase):
    def test_admin_login_fail(self):
        c = Client()
        resp = c.post('/api/a/login',{'username':'wu', 'password':'1234'})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 3)
        self.assertEqual(mess['msg'], 'admin validate error')

class AuthLoginPostSucc(TestCase):
    def test_admin_login_success(self):
        c = Client()
        User.objects.create_user(username='wu',email="dui_zhang@163.com",password='1234')
        resp = c.post('/api/a/login',{'username':'wu', 'password':'1234'})
        mess = json.loads(str(resp.content, encoding = "utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

# class AuthLogoutPost(TestCase):
#     def test_admin_logout(self):
#         c = Client()
#         resp = c.post('/api/a/logout')
#         mess = json.loads(str(resp.content, encoding = "utf-8"))
#         self.assertEqual(mess['code'], 0)
#         self.assertEqual(mess['msg'], '')

# class ActiListGetFail(TestCase):
#     def test_acti_get_fail(self):
#         c = Client()
#         resp = c.post('/api/a/activity/list')
#         mess = json.loads(str(resp.content, encoding = "utf-8"))
#         self.assertEqual(mess['code'], 4)
#         self.assertEqual(mess['msg'], '')

# class ActiListGetSucc(TestCase):
#
#     def test_acti_get_succ(self):
#         url = 'http://140.143.17.33/api/a/login'
#         parms = {'username':'wuhaixu', 'password':'1234qwer'}
#         headers = {
#         'User-agent':'Mozilla/5.0'
#         }
#         resp = requests.post(url,data=parms,headers=headers)
#         mess = json.loads(resp.text)
#         self.assertEqual(mess['code'], 0)
#         self.assertEqual(mess['msg'], '')
#
#         url = 'http://140.143.17.33/api/a/activity/list'
#         parms = {}
#         headers = {
#             'User-agent': 'Mozilla/5.0'
#         }
#         resp = requests.get(url, data=parms, headers=headers)
#         mess = json.loads(resp.text)
#         print ('_____',resp.text)
#         self.assertEqual(mess['code'], 0)
#         self.assertEqual(mess['msg'], '')

# class ActiAdminPageTest(TestCase):
#     def test_admin_list(self):
#         url = 'http://140.143.17.33/api/a/login'
#         parms = {}
#         headers = {
#             'User-agent': 'Mozilla/5.0'
#         }
#         resp = requests.get(url, data=parms, headers=headers)
#         mess = json.loads(resp.text)
#         self.assertEqual(mess['code'], 4)
#         self.assertEqual(mess['msg'], '')
