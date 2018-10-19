from django.test import TestCase, Client
from django.contrib.auth import models
from wechat.models import Activity, Ticket, User
from WeChatTicket.settings import STATIC_ROOT
from django.utils import timezone
import os
import json
import time

c = Client(HTTP_USER_AGENT='Mozilla/5.0')


class AuthLoginGet(TestCase):

    def test_admin_login_get_fail(self):
        resp = c.get('/api/a/login')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

    def test_admin_login_get_succ(self):
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        resp = c.post('/api/a/login', {'username': 'wu', 'password': '1234'})
        resp = c.get('/api/a/login')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')


class AuthLoginPostFail(TestCase):
    def test_admin_login_fail(self):
        resp = c.post('/api/a/login', {'username': 'wu', 'password': '1234'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 3)
        self.assertEqual(mess['msg'], 'admin validate error')

    def test_admin_login_error(self):
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234', is_active=False)
        resp = c.post('/api/a/login', {'username': 'wu', 'password': '1234'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 3)
        self.assertEqual(mess['msg'], 'admin validate error')


class AuthLoginPostSucc(TestCase):

    def test_admin_login_success(self):
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        resp = c.post('/api/a/login', {'username': 'wu', 'password': '1234'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')


class AuthLogout(TestCase):

    def test_admin_get(self):
        resp = c.get('/api/a/logout')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

    def test_admin_logout(self):
        resp = c.post('/api/a/logout', {'arg': 'useless'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')


class ActiListGetFail(TestCase):
    def test_acti_get_fail(self):
        resp = c.get('/api/a/activity/list')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')


class ActiList(TestCase):

    def test_acti_post_succ(self):
        resp = c.post('/api/a/activity/list', {'arg': 'useless'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

    def test_acti_get_succ(self):
        s = Activity(name='11111', key='11', description='aaa',
                     start_time=timezone.now(), end_time=timezone.now(),
                     place='ss', book_end=timezone.now(),
                     book_start=timezone.now(), total_tickets='123',
                     status=Activity.STATUS_PUBLISHED, pic_url='sss', remain_tickets='1')
        s.save()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.get('/api/a/activity/list')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # return empty list
        self.assertEqual(mess['data'][0]['name'], '11111')


class ActiDeleteSucc(TestCase):

    def test_acti_del_get_succ(self):
        resp = c.get('/api/a/activity/delete')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

    def test_acti_del_fail(self):
        s = Activity(name='11111', key='11',
                     description='aaa', start_time=timezone.now(),
                     end_time=timezone.now(), place='ss',
                     book_end=timezone.now(), book_start=timezone.now(),
                     total_tickets='123', status=Activity.STATUS_PUBLISHED,
                     pic_url='sss', remain_tickets='1')
        s.save()
        name_test = s.name
        resp = c.post('/api/a/activity/delete', {'id': s.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')
        t = Activity.objects.filter(name=name_test)
        self.assertEqual(t[0].status, Activity.STATUS_PUBLISHED)

    def test_acti_del_succ(self):
        s = Activity(name='11111', key='11',
                     description='aaa', start_time=timezone.now(),
                     end_time=timezone.now(), place='ss', book_end=timezone.now(),
                     book_start=timezone.now(), total_tickets='123',
                     status=Activity.STATUS_PUBLISHED, pic_url='sss',
                     remain_tickets='1')
        s.save()
        name_test = s.name
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/delete', {'id': s.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        t = Activity.objects.filter(name=name_test)
        self.assertEqual(t[0].status, Activity.STATUS_DELETED)


class ActiCreateSucc(TestCase):
    def test_acti_create_get_succ(self):
        resp = c.get('/api/a/activity/create')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')

    def test_acti_create_post_fail(self):
        resp = c.post('/api/a/activity/create', {'name': '111'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

    def test_acti_create_succ(self):
        tmp = {
            'name': '111',
            'key': 11,
            'place': 'ss',
            'description': 'ss',
            'picUrl': 'ss',
            'startTime': timezone.now(),
            'endTime': timezone.now(),
            'bookStart': timezone.now(),
            'bookEnd': timezone.now(),
            'totalTickets': 'aaa',
            'status': Activity.STATUS_PUBLISHED,
            'remainTickets': '12'
        }
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/create',
                      {'name': '111', 'key': '11', 'place': 'ss',
                       'description': 'ss', 'picUrl': 'ss',
                       'startTime': str(timezone.now()), 'endTime': str(timezone.now()),
                       'bookStart': str(timezone.now()), 'bookEnd': str(timezone.now()),
                       'totalTickets': '123', 'status': Activity.STATUS_PUBLISHED})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        t = Activity.objects.filter(pk=mess['data'])
        self.assertEqual(t[0].name, tmp['name'])

    def test_acti_create_fail_repeat(self):
        a = Activity(name=str(1), key='11', description='aaa', start_time=timezone.now(),
                 end_time=timezone.now(), place='ss', book_end=timezone.now(),
                 book_start=timezone.now(), total_tickets='123', status=Activity.STATUS_PUBLISHED,
                 pic_url='sss',
                 remain_tickets='1')
        a.save()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/create',
                      {'name': a.name, 'key': '11', 'place': 'ss',
                       'description': 'ss', 'picUrl': 'ss',
                       'startTime': a.start_time, 'endTime': str(timezone.now()),
                       'bookStart': str(timezone.now()), 'bookEnd': str(timezone.now()),
                       'totalTickets': '123', 'status': Activity.STATUS_PUBLISHED})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 2)
        self.assertEqual(mess['msg'], 'already have this activity')

class ImageUpFail(TestCase):

    def test_image_up_get(self):
        resp = c.get('/api/a/image/upload/')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 0)
        self.assertEqual(mess['msg'], '')

    def test_image_up_fail(self):
        resp = c.post('/api/a/image/upload/', {'image': 'useless'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 4)
        self.assertEqual(mess['msg'], '')

    def test_image_up_succ(self):
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        path = os.path.join(STATIC_ROOT, 'test.png')
        with open(path, 'rb') as f:
            resp = c.post('/api/a/image/upload/', {'image':f})
            mess = json.loads(str(resp.content, encoding="utf-8"))
            self.assertEqual((mess['code']), 0)
            self.assertEqual(mess['msg'], '')

class ActiDetailTest(TestCase):

    def getTimeStamp(self, str_time):
        return int(time.mktime(str_time.timetuple()))

    def setUp(self):
        s = Activity(name='11111', key='11', description='aaa',
                     start_time=timezone.now(), end_time=timezone.now(),
                     place='ss', book_end=timezone.now(),
                     book_start=timezone.now(), total_tickets='123',
                     status=Activity.STATUS_PUBLISHED, pic_url='sss',
                     remain_tickets='1')
        s.save()

    def test_acti_det_get_fail(self):
        s = Activity.objects.filter(name='11111').first()
        resp = c.get('/api/a/activity/detail', {'id': s.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

    def test_acti_det_get_succ(self):
        s = Activity.objects.filter(name='11111').first()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.get('/api/a/activity/detail', {'id': s.id})
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

    def test_acti_det_mod_fail(self):
        s = Activity.objects.filter(name='11111').first()
        resp = c.post('/api/a/activity/detail', {'id': s.id})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 4)
        self.assertEqual(mess['msg'], '')

    def test_acti_det_mod_succ(self):
        s = Activity.objects.filter(name='11111').first()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/detail', {'id': s.id,
                                                 'name': '11111',
                                                 'place': 'ss',
                                                 'description': 'ss',
                                                 'picUrl': 'to test',
                                                 'startTime': s.start_time,
                                                 'endTime': s.end_time,
                                                 'bookStart': s.book_start,
                                                 'bookEnd': s.book_end,
                                                 'totalTickets': '123',
                                                 'status': Activity.STATUS_PUBLISHED})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # change
        t = Activity.objects.filter(pk=s.id).first()
        self.assertEqual(t.pic_url, 'to test')

    def test_acti_det_mod_statusFail(self):
        s = Activity.objects.filter(name='11111').first()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/detail', {'id': s.id,
                                                 'name': 'to test',
                                                 'place': 'to test',
                                                 'description': 'ss',
                                                 'picUrl': 'sss',
                                                 'startTime': s.start_time,
                                                 'endTime': s.end_time,
                                                 'bookStart': timezone.now(),
                                                 'bookEnd': s.book_end,
                                                 'totalTickets': '123',
                                                 'status': Activity.STATUS_PUBLISHED})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # no change
        t = Activity.objects.filter(pk=s.id).first()
        self.assertEqual(t.name, '11111')
        self.assertEqual(t.place, 'ss')
        self.assertEqual(t.book_start, s.book_start)

    def test_acti_det_mod_timeFail(self):
        s = Activity.objects.filter(name='11111').first()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/detail', {'id': s.id,
                                                 'name': '11111',
                                                 'place': 'ss',
                                                 'description': 'ss',
                                                 'picUrl': 'to test',
                                                 'startTime': 'ssss',
                                                 'endTime': 'ssss',
                                                 'bookStart': s.book_start,
                                                 'bookEnd': 'ssss',
                                                 'totalTickets': '2333333',
                                                 'status': Activity.STATUS_PUBLISHED})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual(mess['code'], 0)
        self.assertEqual(mess['msg'], '')
        # no change
        t = Activity.objects.filter(pk=s.id).first()
        self.assertEqual(t.pic_url, 'to test')
        self.assertEqual(t.total_tickets, 123)
        self.assertEqual(t.start_time, s.start_time)
        self.assertEqual(t.end_time, s.end_time)
        self.assertEqual(t.book_end, s.book_end)


class ActiMenuTest(TestCase):

    def test_acti_menu_get_succ(self):
        s = []
        for i in range(6):
            s.append(Activity(name=str(i), key='11', description='aaa', start_time=timezone.now(),
                              end_time=timezone.now(), place='ss', book_end=timezone.now(),
                              book_start=timezone.now(), total_tickets='123', status=Activity.STATUS_PUBLISHED,
                              pic_url='sss',
                              remain_tickets='1'))
            s[i].save()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.get('/api/a/activity/menu/', {'arg': 'useless'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 0)
        self.assertEqual(mess['msg'], '')
        m = mess['data']
        for i in range(len(m)):
            self.assertEqual(m[i]['name'], str(i))

    def test_acti_menu_get_fail(self):
        s = []
        for i in range(6):
            s.append(Activity(name=str(i), key='11', description='aaa', start_time=timezone.now(),
                              end_time=timezone.now(), place='ss', book_end=timezone.now(),
                              book_start=timezone.now(), total_tickets='123', status=Activity.STATUS_PUBLISHED,
                              pic_url='sss',
                              remain_tickets='1'))
            s[i].save()
        resp = c.get('/api/a/activity/menu/', {'arg': 'useless'})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 4)
        self.assertEqual(mess['msg'], '')

    def test_acti_menu_post_fail(self):
        s = []
        for i in range(6):
            s.append(Activity(name=str(i), key='11', description='aaa', start_time=timezone.now(),
                              end_time=timezone.now(), place='ss', book_end=timezone.now(),
                              book_start=timezone.now(), total_tickets='123', status=Activity.STATUS_PUBLISHED,
                              pic_url='sss',
                              remain_tickets='1'))
            s[i].save()
        resp = c.post('/api/a/activity/menu/', {'id': [1, 2, 3, 4]})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 4)
        self.assertEqual(mess['msg'], '')


class CheckInTest(TestCase):
    def setUp(self):
        for i in range(6):
            u = User(open_id=str(i), student_id=str(i))
            u.save()
        a = Activity(name=str(1), key='11', description='aaa', start_time=timezone.now(),
                     end_time=timezone.now(), place='ss', book_end=timezone.now(),
                     book_start=timezone.now(), total_tickets='123', status=Activity.STATUS_PUBLISHED, pic_url='sss',
                     remain_tickets='1')
        a.save()

    def test_checkin_get_succ(self):
        resp = c.get('/api/a/activity/checkin/')
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 0)
        self.assertEqual(mess['msg'], '')

    def test_checkin_fail(self):
        a = Activity.objects.filter(name='1').first()
        t = []
        for i in range(6):
            t.append(
                Ticket(id=i + 1, student_id=str(i), unique_id=str(i + 1), status=Ticket.STATUS_VALID, activity_id=a.id))
            t[i].save()
        resp = c.post('/api/a/activity/checkin/', {'actId': 0, 'studentId': 1})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 4)
        self.assertEqual(mess['msg'], '')

    def test_checkin_fail_ticketUsed(self):
        a = Activity.objects.filter(name='1').first()
        t = []
        for i in range(6):
            t.append(
                Ticket(id=i + 1, student_id=str(i), unique_id=str(i + 1), status=Ticket.STATUS_USED, activity_id=a.id))
            t[i].save()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/checkin/', {'actId': 0, 'studentId': 1})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 2)
        self.assertEqual(mess['msg'], '检票失败')

    def test_checkin_fail_noStudent(self):
        a = Activity.objects.filter(name='1').first()
        t = []
        for i in range(3):
            t.append(
                Ticket(id=i + 1, student_id=str(i), unique_id=str(i + 1), status=Ticket.STATUS_USED, activity_id=a.id))
            t[i].save()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/checkin/', {'actId': 0, 'studentId': 10})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 2)
        self.assertEqual(mess['msg'], '检票失败')

    def test_checkin_succ(self):
        a = Activity.objects.filter(name='1').first()
        t = []
        for i in range(6):
            t.append(
                Ticket(id=i + 1, student_id=str(i), unique_id=str(i + 1), status=Ticket.STATUS_VALID, activity_id=a.id))
            t[i].save()
        models.User.objects.create_user(username='wu', email="dui_zhang@163.com", password='1234')
        c.login(username='wu', password='1234')
        resp = c.post('/api/a/activity/checkin/', {'actId': a.id, 'studentId': str(1)})
        mess = json.loads(str(resp.content, encoding="utf-8"))
        self.assertEqual((mess['code']), 0)
        self.assertEqual(mess['msg'], '')
        m = Ticket.objects.filter(unique_id=mess['data']['ticket']).first()
        self.assertEqual(m.status, Ticket.STATUS_USED)
