from django.test import TestCase
from wechat.models import *
import requests
import json
# Create your tests here.

class UserBindTest(TestCase):

    def test(self):
        u1 = User.objects.create(open_id='abc')
        u1.save()
        u2 = User.objects.create(open_id='a', student_id='2016013224')
        u2.save()
        url = 'http://127.0.0.1:8000/api/u/user/bind/'

        parms = {'openid': 'abc'}
        resp = requests.get(url, parms)
        mess = json.loads(resp.text)
        print(mess)
        #self.assertEqual(mess['code'], 3)
        #self.assertEqual(mess['msg'], 'admin validate error')
        parms = {'openid': 'a'}
        resp = requests.get(url, parms)
        mess = json.loads(resp.text)
        print(mess)

        parms = {'openid':'abc','student_id':'2016013225','password':'abc'}
        resp = requests.post(url, parms)
        mess = json.loads(resp.text)
        print(mess)

        parms = {'openid': 'a'}
        resp = requests.get(url, parms)
        mess = json.loads(resp.text)
        print(mess)
