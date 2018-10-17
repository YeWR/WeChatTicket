from django.test import TestCase, Client,RequestFactory
from wechat.models import *
import userpage.views as views
import json
# Create your tests here.

class UserBindTest(TestCase):

    def testUserBind(self):
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013224')
        print(User.get_by_openid('abc').open_id)
        print(User.get_by_openid('a').open_id)
        c = Client()
        resp = c.get("/api/u/user/bind", {'openid': 'a'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['data'], '2016013224')

        resp = c.get("/api/u/user/bind", {'openid': 'abc'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['data'], '')

        parms = {'openid':'abc','student_id':'2016013225','password':'abc'}
        resp = c.post("/api/u/user/bind", parms)
        mess = json.loads(str(resp.content, encoding="utf-8"))

        parms = {'openid': 'abc'}
        resp = c.get("/api/u/user/bind", parms)
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['data'], '2016013225')

        resp = c.get("/api/u/user/bind", {'openid': 'def'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 2)
