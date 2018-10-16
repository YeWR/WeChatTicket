from django.test import TestCase
from django.contrib.auth.models import User
from . import views as views
import requests
import json

class AdminPageTest(TestCase):
    def test_admin_login_fail(self):
        # model to post 
        url = 'http://127.0.0.1/api/a/login'
        parms = {'username':'wu', 'password':'1234'}
        headers = {
        'User-agent':'Mozilla/5.0'
        }
        resp = requests.post(url,data=parms,headers=headers)
        mess = json.loads(resp.text)
        self.assertEqual(mess['code'], 3)
        self.assertEqual(mess['msg'], 'admin validate error')

    def test_admin_login_success(self):
        # model to post 
        user = User.objects.create_user('wu','','1234')
        user.save()
        url = 'http://127.0.0.1/api/a/login'
        parms = {'username':'wu', 'password':'1234'}
        headers = {
        'User-agent':'Mozilla/5.0'
        }
        resp = requests.post(url,data=parms,headers=headers)
        mess = json.loads(resp.text)
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')       

    def test_admin_logout(self):
        pass



# class AnimalTestCase(TestCase):

#     def test_animals_can_speak(self):

#         """add test demo"""

#         testNum = 4
#         x = []
#         y = []
#         ans = []
#         for i in range(0, testNum):
#             x.append(i)
#             y.append(2 * i)
#             ans.append(3 * i)
#         for i in range(0, testNum):
#             self.assertEqual(views.testDemoAdd(x[i], y[i]), ans[i])