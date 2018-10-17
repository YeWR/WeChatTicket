from django.test import TestCase, Client
from wechat.models import *
import json
# Create your tests here.

class UserBindTest(TestCase):

    def testUserBind(self):
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013224')
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
        #should raise User not found
        resp = c.get("/api/u/user/bind", {'openid': 'def'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 2)

class ActivityDetailTest(TestCase):

    def testActivityDetail_published(self):
        act = Activity.objects.create(name='abc',key='abcd',description='abcde',start_time='2016-06-03 13:00:00',end_time='2016-06-03 13:00:00',
                                place='aaa',book_start='2016-06-03 13:00:00',book_end='2016-06-03 13:00:00',total_tickets=100,pic_url='http',
                                remain_tickets=50,status=1)
        c = Client()
        resp = c.get("/api/u/activity/detail", {'id': act.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)

    def testActivityDetail_unpublished(self):
        #should raise Activity not published
        act = Activity.objects.create(name='abc', key='abcd', description='abcde', start_time='2016-06-03 13:00:00', end_time='2016-06-03 13:00:00',
                                place='aaa', book_start='2016-06-03 13:00:00', book_end='2016-06-03 13:00:00', total_tickets=100, pic_url='http',
                                remain_tickets=50, status=0)
        c = Client()
        resp = c.get("/api/u/activity/detail", {'id': act.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertNotEqual(mess['code'], 0)

class TicketDetailTest(TestCase):

    def testTicketDetail(self):
        User.objects.create(open_id='a', student_id='2016013224')
        Activity.objects.create(name='abc', key='abcd', description='abcde', start_time='2016-06-03 13:00:00', end_time='2016-06-03 13:00:00',
                                place='aaa', book_start='2016-06-03 13:00:00', book_end='2016-06-03 13:00:00', total_tickets=100, pic_url='http',
                                remain_tickets=50, status=1)
        Ticket.objects.create(student_id='2016013224', unique_id=10010, activity=Activity.objects.get(name='abc'),status=1)
        c = Client()
        resp = c.get("/api/u/ticket/detail", {'openid': 'a', 'ticket': 10010})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['data']['uniqueID'], '10010')