# -*- coding: utf-8 -*-
#
import random
import string

from django.test import TestCase, Client
from django.utils import timezone
from WeChatTicket import settings
from wechat.models import *
from wechat.views import CustomWeChatView
# import requests
import time
import datetime
import re

c = Client(HTTP_USER_AGENT='Mozilla/5.0')

'''
文本消息xml模板
<xml>  
<ToUserName>< ![CDATA[wxid_72hqnxt2zzy322] ]></ToUserName>  
<FromUserName>< ![CDATA[{fromUser}] ]></FromUserName>  
<CreateTime>{curTime}</CreateTime>  
<MsgType>< ![CDATA[text] ]></MsgType>  
<Content>< ![CDATA[{textMsg}] ]></Content>  
<MsgId>{msgId}</MsgId>  
</xml>
'''

'''
自定义菜单事件xml模板
<xml>
<ToUserName><![CDATA[wxid_72hqnxt2zzy322]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{curTime}</CreateTime>
<MsgType><![CDATA[event]]></MsgType>
<Event><![CDATA[CLICK]]></Event>
<EventKey><![CDATA[{EVENTKEY}]]></EventKey>
</xml>
'''


def getTimeStamp(timeObj):
    return int(time.mktime(timeObj.timetuple()))


def getTextXml(fromUser, curTime, textMsg, msgId):
    xml = \
        '''
        <xml>
        <ToUserName><![CDATA[wxid_72hqnxt2zzy322]]></ToUserName>
        <FromUserName><![CDATA[{fromUser}]]></FromUserName>
        <CreateTime>{curTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{textMsg}]]></Content>
        <MsgId>{msgId}</MsgId>
        </xml>'''.format(fromUser=fromUser, curTime=curTime, textMsg=textMsg, msgId=msgId)
    return xml


def getClickXml(fromUser, curTime, eventKey):
    xml = \
        '''
        <xml>
        <ToUserName><![CDATA[wxid_72hqnxt2zzy322]]></ToUserName>
        <FromUserName><![CDATA[{fromUser}]]></FromUserName>
        <CreateTime>{curTime}</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[CLICK]]></Event>
        <EventKey><![CDATA[{eventKey}]]></EventKey>
        </xml>'''.format(fromUser=fromUser, curTime=curTime, eventKey=eventKey)
    return xml


class TestError(TestCase):
    pass


class TestDefault(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['balabala', 'gg', '抢火车票']

    # 是否返回帮助
    def is_default(self, content):
        pattern = '对不起，没有找到您需要的信息:('
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()

        for user in users:
            for textMsg in self.textMsgs:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, textMsg, msgId)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                self.assertEqual(self.is_default(content), True)


class TestHelpOrSubscribe(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['帮助', 'Help', 'help', 'HELP']

        # clickEvents => 用户一般可能点击事件
        self.clickEvents = [CustomWeChatView.event_keys['help']]

    # 是否返回帮助
    def is_help(self, content):
        pattern = '“紫荆之声”使用指南'
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()

        for user in users:
            for textMsg in self.textMsgs:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, textMsg, msgId)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                self.assertEqual(self.is_help(content), True)

    def test_event(self):
        pass

    def test_event_click(self):
        users = User.objects.all()

        for user in users:
            for clickEvent in self.clickEvents:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                data = getClickXml(fromUser, curTime, clickEvent)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                self.assertEqual(self.is_help(content), True)


class TestUnbindOrUnsubscribe(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['解绑']

    # 未解绑用户
    def is_unbind(self, content):
        pattern = '对不起，您还没有绑定，不能解绑'
        return content.find(pattern) != -1

    # 解绑用户
    def is_bind(self, content):
        pattern = '学号绑定已经解除'
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()

        for user in users:
            for textMsg in self.textMsgs:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, textMsg, msgId)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                # 绑定用户
                if user.student_id:
                    self.assertEqual(self.is_bind(content), True)
                else:
                    self.assertEqual(self.is_unbind(content), True)


class TestBindAccount(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['绑定']

        # clickEvents => 用户一般可能点击事件
        self.clickEvents = [CustomWeChatView.event_keys['account_bind']]

    # 未解绑用户
    def is_unbind(self, content):
        pattern = '请点击下方链接进行学号绑定'
        return content.find(pattern) != -1

    # 解绑用户
    def is_bind(self, content):
        pattern = '您已经绑定了学号'
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()
        for user in users:
            for textMsg in self.textMsgs:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, textMsg, msgId)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                # 绑定用户
                if user.student_id:
                    self.assertEqual(self.is_bind(content), True)
                else:
                    self.assertEqual(self.is_unbind(content), True)

    def test_event_click(self):
        users = User.objects.all()

        for user in users:
            for clickEvent in self.clickEvents:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                data = getClickXml(fromUser, curTime, clickEvent)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                # 绑定用户
                if user.student_id:
                    self.assertEqual(self.is_bind(content), True)
                else:
                    self.assertEqual(self.is_unbind(content), True)


class TestBookEmpty(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

    def test_text(self):
        pass

    def test_event_click(self):
        pass


def createActivities(num=0):
    for i in range(num):
        # total ticket: i
        # state: Activity.STATUS_PUBLISHED
        # remain tickets: random.randint(0, num)
        Activity.objects.create(name=str(i), key=str(2 * i), description=str(3 * i),
                                start_time=timezone.now(), \
                                end_time=timezone.now(), place=str(4 * i), book_end=timezone.now(), \
                                book_start=timezone.now(), total_tickets=str(i),
                                status=str(Activity.STATUS_PUBLISHED), pic_url='sss',
                                remain_tickets=str(random.randint(0, i)))


# 抢啥
class TestBookWhat(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['抢啥']

        # clickEvents => 用户一般可能点击事件
        self.clickEvents = [CustomWeChatView.event_keys['book_what']]

    #  有活动
    def is_activities(self, content):
        pattern = re.compile(
            r'<Title><!\[CDATA\[[\w\W\u4e00-\u9fff]{4}：(\d+)\n[\w\W\u4e00-\u9fff]{4}：(\d+)\n[\w\W\u4e00-\u9fff]{4}：(\d\d\d\d-\d\d-\d\d.*)-(\d\d\d\d-\d\d-\d\d.*)\]\]></Title>',
            re.M)
        data = pattern.finditer(content, re.M)
        if not data:
            return False
        for dt in data:
            name = str(dt.group(1))
            # 剩余数量会一直变，因此不需要
            # remain_tickets = str(dt.group(2))
            start_time = str(dt.group(3))
            end_time = str(dt.group(4))
            # 是否有这样的活动
            act = Activity.objects.filter(name=name, start_time=start_time,
                                          end_time=end_time, status=Activity.STATUS_PUBLISHED)
            if not act:
                return False
        return True

    # 无活动
    def no_activities(self, content):
        pattern = '您好，现在没有推荐的抢票活动哟'
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()

        # 活动
        maxActivities = 2
        while len(Activity.objects.all()) < maxActivities:
            # no activity
            for user in users:
                for textMsg in self.textMsgs:
                    fromUser = user.open_id
                    curTime = str(getTimeStamp(datetime.datetime.now()))
                    msgId = str(random.randint(0, 99999)) + curTime
                    data = getTextXml(fromUser, curTime, textMsg, msgId)

                    response = self.client.post(
                        path='/wechat/',
                        content_type='application/xml',
                        data=data
                    )

                    content = str(response.content.decode('utf-8'))
                    # 有活动
                    if Activity.objects.all():
                        self.assertEqual(self.is_activities(content), True)
                    else:
                        self.assertEqual(self.no_activities(content), True)
            # add activities
            createActivities(maxActivities - 1)

    def test_event_click(self):
        users = User.objects.all()

        # 活动
        maxActivities = 3
        while len(Activity.objects.all()) < maxActivities:
            # no activity
            for user in users:
                for clickEvent in self.clickEvents:
                    fromUser = user.open_id
                    curTime = str(getTimeStamp(datetime.datetime.now()))
                    data = getClickXml(fromUser, curTime, clickEvent)

                    response = self.client.post(
                        path='/wechat/',
                        content_type='application/xml',
                        data=data
                    )

                    content = str(response.content.decode('utf-8'))
                    # 有活动
                    if Activity.objects.all():
                        self.assertEqual(self.is_activities(content), True)
                    else:
                        self.assertEqual(self.no_activities(content), True)
            # add activities
            createActivities(maxActivities - 1)


# 查票
class TestCheckTicket(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['查票']

        # clickEvents => 用户一般可能点击事件
        self.clickEvents = [CustomWeChatView.event_keys['get_ticket']]

    def book_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        Ticket.objects.create(student_id=str(user.student_id), unique_id=str(random.randint(0, 9999999)),
                              activity=activity,
                              status=Ticket.STATUS_VALID)
        activity.remain_tickets -= 1
        activity.save()

    # 未绑用户
    def is_unbind(self, content):
        pattern = '请点击下方链接进行学号绑定'
        return content.find(pattern) != -1

    # 有票绑定用户
    def is_bind_and_tickets(self, content):
        pattern = re.compile(
            r'<Title><!\[CDATA\[[\w\W\u4e00-\u9fff]{4}：(\d+)\n[\w\W\u4e00-\u9fff]{4}：(\d+)\n[\w\W\u4e00-\u9fff]{4}：(\d\d\d\d-\d\d-\d\d.*)-(\d\d\d\d-\d\d-\d\d.*)\]\]></Title>',
            re.M)
        data = pattern.finditer(content, re.M)
        if not data:
            return False
        for dt in data:
            name = str(dt.group(1))
            # 剩余数量会一直变，因此不需要
            # remain_tickets = str(dt.group(2))
            start_time = str(dt.group(3))
            end_time = str(dt.group(4))
            # 是否有这样的活动
            act = Activity.objects.filter(name=name, start_time=start_time,
                                          end_time=end_time, status=Activity.STATUS_PUBLISHED)
            if not act:
                return False
        return True

    def is_bind_no_tickets(self, content):
        pattern = '亲~您目前没有有效的订票哟~'
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()

        # 活动
        maxActivities = 2
        createActivities(maxActivities)

        for user in users:
            # flag 0-> 没买票
            # flag 1-> 买了票
            for flag in range(2):
                for textMsg in self.textMsgs:
                    fromUser = user.open_id
                    curTime = str(getTimeStamp(datetime.datetime.now()))
                    msgId = str(random.randint(0, 99999)) + curTime
                    data = getTextXml(fromUser, curTime, textMsg, msgId)

                    response = self.client.post(
                        path='/wechat/',
                        content_type='application/xml',
                        data=data
                    )

                    content = str(response.content.decode('utf-8'))
                    if not user.student_id:
                        self.assertEqual(self.is_unbind(content), True)
                    elif not flag:
                        # 没票
                        self.assertEqual(self.is_bind_no_tickets(content), True)
                        # 买票
                        for act in Activity.objects.all():
                            self.book_ticket(user, act.name)
                    else:
                        self.assertEqual(self.is_bind_and_tickets(content), True)

    def test_event_click(self):
        users = User.objects.all()

        # 活动
        maxActivities = 2
        createActivities(maxActivities)

        for user in users:
            # flag 0-> 没买票
            # flag 1-> 买了票
            for flag in range(2):
                for clickEvent in self.clickEvents:
                    fromUser = user.open_id
                    curTime = str(getTimeStamp(datetime.datetime.now()))
                    data = getClickXml(fromUser, curTime, clickEvent)

                    response = self.client.post(
                        path='/wechat/',
                        content_type='application/xml',
                        data=data
                    )

                    content = str(response.content.decode('utf-8'))
                    if not user.student_id:
                        self.assertEqual(self.is_unbind(content), True)
                    elif not flag:
                        # 没票
                        self.assertEqual(self.is_bind_no_tickets(content), True)
                        # 买票
                        for act in Activity.objects.all():
                            self.book_ticket(user, act.name)
                    else:
                        self.assertEqual(self.is_bind_and_tickets(content), True)


# 抢票
class TestBookTicket(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['抢票']
        self.clickEvents = [CustomWeChatView.event_keys['book_header'] + '999999']
        for i in range(1, 8):
            self.textMsgs.append('抢票 ' + str(i))

        # clickEvents => 用户一般可能点击事件

        # 活动，此处如果修改注意相应的textMsgs也要修改
        # 取消
        act = Activity.objects.create(name='1', key='abcd', description='abcde', start_time='2016-06-03 13:00:00',
                                      end_time='2016-06-03 13:00:00',
                                      place='aaa', book_start='2016-06-03 13:00:00', book_end='2016-06-03 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_DELETED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))

        # 未发布
        act = Activity.objects.create(name='2', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_SAVED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))
        # 未开始
        act = Activity.objects.create(name='3', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2019-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))
        # 已结束
        act = Activity.objects.create(name='4', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2018-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))
        # 已售空
        act = Activity.objects.create(name='5', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=0, status=Activity.STATUS_PUBLISHED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))
        # 设置为已购票
        self.bought_name = 6
        # 已购票
        act = Activity.objects.create(name=str(self.bought_name), key='abcd', description='abcde',
                                      start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))
        # 设置为已购票
        self.used_name = 7
        # 已使用过票
        act = Activity.objects.create(name=str(self.used_name), key='abcd', description='abcde',
                                      start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        self.clickEvents.append(CustomWeChatView.event_keys['book_header'] + str(act.id))

    # 抢票
    def book_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        Ticket.objects.create(student_id=str(user.student_id), unique_id=str(random.randint(0, 9999999)),
                              activity=activity,
                              status=Ticket.STATUS_VALID)
        activity.remain_tickets -= 1
        activity.save()

    # 使用票
    def use_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        ticket = Ticket.objects.filter(student_id=user.student_id, activity=activity).first()
        ticket.status = Ticket.STATUS_USED
        ticket.save()

    # 退票
    def cancle_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        ticket = Ticket.objects.filter(student_id=user.student_id, activity=activity).first()
        ticket.status = Ticket.STATUS_CANCELLED
        activity.remain_tickets += 1
        ticket.save()
        activity.save()

    # 未绑用户
    def is_unbind(self, content):
        pattern = '请点击下方链接进行学号绑定'
        return content.find(pattern) != -1

    def no_activity(self, content):
        pattern = '对不起，不存在该活动！'
        return content.find(pattern) != -1

    def cancled_activity(self, content):
        pattern = '对不起，该活动已取消！'
        return content.find(pattern) != -1

    def notPublished_activity(self, content):
        pattern = '对不起，该活动还未发布！'
        return content.find(pattern) != -1

    def notStart_activity(self, content):
        pattern = '对不起，抢票尚未开始！'
        return content.find(pattern) != -1

    def end_activity(self, content):
        pattern = '对不起，抢票已结束！'
        return content.find(pattern) != -1

    def no_ticket(self, content):
        pattern = '对不起，票已售空！'
        return content.find(pattern) != -1

    def bought_ticket(self, content):
        pattern = '对不起，您已购过票！'
        return content.find(pattern) != -1

    def used_ticket(self, content):
        pattern = '对不起，您已使用过票！'
        return content.find(pattern) != -1

    #
    def map_ticket(self, content, type):
        if type == 0:
            return self.no_activity(content)
        elif type == 1:
            return self.cancled_activity(content)
        elif type == 2:
            return self.notPublished_activity(content)
        elif type == 3:
            return self.notStart_activity(content)
        elif type == 4:
            return self.end_activity(content)
        elif type == 5:
            return self.no_ticket(content)
        elif type == 6:
            return self.bought_ticket(content)
        elif type == 7:
            return self.used_ticket(content)
        else:
            return False

    # 新票
    def book_success(self, content):
        pattern = re.compile(
            r'<Title><!\[CDATA\[([\d]*)，您好！([\w\W\u4e00-\u9fff]*)已抢票成功！（新票）\]\]></Title>',
            re.M)
        data = pattern.finditer(content, re.M)
        if not data:
            return False
        for dt in data:
            stu_id = dt.group(1)
            act_name = dt.group(2)
            # 是否有这样的票
            ticket = Ticket.objects.filter(student_id=stu_id, activity__name=act_name, status=Ticket.STATUS_VALID)
            if not ticket:
                return False
        return True

    # 重购票
    def rebook_success(self, content):
        pattern = re.compile(
            r'<Title><!\[CDATA\[([\d]*)，您好！([\w\W\u4e00-\u9fff]*)已抢票成功！（重购此票）\]\]></Title>',
            re.M)
        data = pattern.finditer(content, re.M)
        if not data:
            return False
        for dt in data:
            stu_id = dt.group(1)
            act_name = dt.group(2)
            # 是否有这样的票
            ticket = Ticket.objects.filter(student_id=stu_id, activity__name=act_name, status=Ticket.STATUS_VALID)
            if not ticket:
                return False
        return True

    def test_text(self):
        users = User.objects.all()

        # 购票失败
        for user in users:
            type = 0
            if user.student_id:
                self.book_ticket(user, self.bought_name)
                self.book_ticket(user, self.used_name)
                self.use_ticket(user, self.used_name)
            for textMsg in self.textMsgs:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, textMsg, msgId)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                if not user.student_id:
                    self.assertEqual(self.is_unbind(content), True)
                else:
                    self.assertEqual(self.map_ticket(content, type), True)
                type += 1

        # 购票成功
        # 购买新票
        act = Activity.objects.create(name=str(len(self.textMsgs) + 1), key='abcd', description='abcde',
                                      start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        msg = "抢票 " + str(len(self.textMsgs) + 1)
        for user in users:
            # 0->新票
            # 1->重购票
            for flag in range(2):
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, msg, msgId)

                # 剩余票数
                remain_tickets_previous = act.remain_tickets

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                if not user.student_id:
                    self.assertEqual(self.is_unbind(content), True)
                elif not flag:
                    self.assertEqual(self.book_success(content), True)
                    # 剩余票数
                    act = Activity.objects.filter(name=str(len(self.textMsgs) + 1)).first()
                    remain_tickets_current = act.remain_tickets

                    self.assertEqual(remain_tickets_current, remain_tickets_previous - 1)
                    remain_tickets_previous = remain_tickets_current
                    # 取消票
                    self.cancle_ticket(user, str(len(self.textMsgs) + 1))
                    act = Activity.objects.filter(name=str(len(self.textMsgs) + 1)).first()
                    # 剩余票数
                    remain_tickets_current = act.remain_tickets
                    self.assertEqual(remain_tickets_current, remain_tickets_previous + 1)
                else:
                    # 重购票
                    self.assertEqual(self.rebook_success(content), True)
                    # 剩余票数
                    act = Activity.objects.filter(name=str(len(self.textMsgs) + 1)).first()
                    remain_tickets_current = act.remain_tickets
                    self.assertEqual(remain_tickets_current, remain_tickets_previous - 1)

    def test_event_click(self):
        users = User.objects.all()

        # 购票失败
        for user in users:
            type = 0
            if user.student_id:
                self.book_ticket(user, self.bought_name)
                self.book_ticket(user, self.used_name)
                self.use_ticket(user, self.used_name)
            for clickEvent in self.clickEvents:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                data = getClickXml(fromUser, curTime, clickEvent)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                if not user.student_id:
                    self.assertEqual(self.is_unbind(content), True)
                else:
                    self.assertEqual(self.map_ticket(content, type), True)
                type += 1

        # 购票成功
        # 购买新票
        act = Activity.objects.create(name=str(len(self.clickEvents) + 1), key='abcd', description='abcde',
                                      start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        clickEvent = CustomWeChatView.event_keys['book_header'] + str(act.id)
        for user in users:
            # 0->新票
            # 1->重购票
            for flag in range(2):
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                data = getClickXml(fromUser, curTime, clickEvent)

                # 剩余票数
                remain_tickets_previous = act.remain_tickets

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                if not user.student_id:
                    self.assertEqual(self.is_unbind(content), True)
                elif not flag:
                    self.assertEqual(self.book_success(content), True)
                    # 剩余票数
                    act = Activity.objects.filter(name=str(len(self.clickEvents) + 1)).first()
                    remain_tickets_current = act.remain_tickets

                    self.assertEqual(remain_tickets_current, remain_tickets_previous - 1)
                    remain_tickets_previous = remain_tickets_current
                    # 取消票
                    self.cancle_ticket(user, str(len(self.clickEvents) + 1))
                    act = Activity.objects.filter(name=str(len(self.clickEvents) + 1)).first()
                    # 剩余票数
                    remain_tickets_current = act.remain_tickets
                    self.assertEqual(remain_tickets_current, remain_tickets_previous + 1)
                else:
                    # 重购票
                    self.assertEqual(self.rebook_success(content), True)
                    # 剩余票数
                    act = Activity.objects.filter(name=str(len(self.clickEvents) + 1)).first()
                    remain_tickets_current = act.remain_tickets
                    self.assertEqual(remain_tickets_current, remain_tickets_previous - 1)


class TestRefundTicket(TestCase):

    def setUp(self):
        # 设置配置
        settings.IGNORE_WECHAT_SIGNATURE = True

        # user1 => not bind
        # user2 => bind
        User.objects.create(open_id='abc')
        User.objects.create(open_id='a', student_id='2016013265')

        # textMsgs => 用户一般可能输入(成功)
        self.textMsgs = ['退票']
        for i in range(1, 8):
            self.textMsgs.append('退票 ' + str(i))

        # 活动，此处如果修改注意相应的textMsgs也要修改
        # 取消
        Activity.objects.create(name='1', key='abcd', description='abcde', start_time='2016-06-03 13:00:00',
                                end_time='2016-06-03 13:00:00',
                                place='aaa', book_start='2016-06-03 13:00:00', book_end='2016-06-03 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=50, status=Activity.STATUS_DELETED)

        # 未发布
        Activity.objects.create(name='2', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                end_time='2019-06-04 13:00:00',
                                place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=50, status=Activity.STATUS_SAVED)
        # 未开始
        Activity.objects.create(name='3', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                end_time='2019-06-04 13:00:00',
                                place='aaa', book_start='2019-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        # 已结束
        Activity.objects.create(name='4', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                end_time='2019-06-04 13:00:00',
                                place='aaa', book_start='2018-06-03 13:00:00', book_end='2018-06-04 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        # 未购票
        Activity.objects.create(name='5', key='abcd', description='abcde', start_time='2018-06-03 13:00:00',
                                end_time='2019-06-04 13:00:00',
                                place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=0, status=Activity.STATUS_PUBLISHED)
        # 设置为已退票
        self.refund_name = 6
        # 已退票
        Activity.objects.create(name=str(self.refund_name), key='abcd', description='abcde',
                                start_time='2018-06-03 13:00:00',
                                end_time='2019-06-04 13:00:00',
                                place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        # 设置为已使用过票
        self.used_name = 7
        # 已使用过票
        Activity.objects.create(name=str(self.used_name), key='abcd', description='abcde',
                                start_time='2018-06-03 13:00:00',
                                end_time='2019-06-04 13:00:00',
                                place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                total_tickets=100, pic_url='http',
                                remain_tickets=50, status=Activity.STATUS_PUBLISHED)

    # 抢票
    def book_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        Ticket.objects.create(student_id=str(user.student_id), unique_id=str(random.randint(0, 9999999)),
                              activity=activity,
                              status=Ticket.STATUS_VALID)
        activity.remain_tickets -= 1
        activity.save()

    # 使用票
    def use_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        ticket = Ticket.objects.filter(student_id=user.student_id, activity=activity).first()
        ticket.status = Ticket.STATUS_USED
        ticket.save()

    # 退票
    def cancle_ticket(self, user, act_name):
        activity = Activity.objects.filter(name=act_name).first()
        ticket = Ticket.objects.filter(student_id=user.student_id, activity=activity).first()
        ticket.status = Ticket.STATUS_CANCELLED
        activity.remain_tickets += 1
        ticket.save()
        activity.save()

    # 未绑用户
    def is_unbind(self, content):
        pattern = '请点击下方链接进行学号绑定'
        return content.find(pattern) != -1

    def no_activity(self, content):
        pattern = '对不起，不存在该活动，无法退票！'
        return content.find(pattern) != -1

    def cancled_activity(self, content):
        pattern = '对不起，该活动已取消，无法退票！'
        return content.find(pattern) != -1

    def notPublished_activity(self, content):
        pattern = '对不起，该活动还未发布，无法退票！'
        return content.find(pattern) != -1

    def notStart_activity(self, content):
        pattern = '对不起，抢票尚未开始，无法退票！'
        return content.find(pattern) != -1

    def end_activity(self, content):
        pattern = '对不起，抢票已结束，无法退票！'
        return content.find(pattern) != -1

    def no_ticket(self, content):
        pattern = '对不起，您尚未购票，无法退票！'
        return content.find(pattern) != -1

    def refunded_ticket(self, content):
        pattern = '对不起，您已退过此票，无法退票！'
        return content.find(pattern) != -1

    def used_ticket(self, content):
        pattern = '对不起，您已使用过此票，无法退票！'
        return content.find(pattern) != -1

    #
    def map_ticket(self, content, type):
        if type == 0:
            return self.no_activity(content)
        elif type == 1:
            return self.cancled_activity(content)
        elif type == 2:
            return self.notPublished_activity(content)
        elif type == 3:
            return self.notStart_activity(content)
        elif type == 4:
            return self.end_activity(content)
        elif type == 5:
            return self.no_ticket(content)
        elif type == 6:
            return self.refunded_ticket(content)
        elif type == 7:
            return self.used_ticket(content)
        else:
            return False

    def refund_success(self, content):
        pattern = '您已成功退票！'
        return content.find(pattern) != -1

    def test_text(self):
        users = User.objects.all()

        # 退票失败
        for user in users:
            type = 0
            if user.student_id:
                # 退票
                self.book_ticket(user, self.refund_name)
                self.cancle_ticket(user, self.refund_name)
                # 使用票
                self.book_ticket(user, self.used_name)
                self.use_ticket(user, self.used_name)
            for textMsg in self.textMsgs:
                fromUser = user.open_id
                curTime = str(getTimeStamp(datetime.datetime.now()))
                msgId = str(random.randint(0, 99999)) + curTime
                data = getTextXml(fromUser, curTime, textMsg, msgId)

                response = self.client.post(
                    path='/wechat/',
                    content_type='application/xml',
                    data=data
                )

                content = str(response.content.decode('utf-8'))
                if not user.student_id:
                    self.assertEqual(self.is_unbind(content), True)
                else:
                    self.assertEqual(self.map_ticket(content, type), True)
                type += 1

        # 退票成功
        act = Activity.objects.create(name=str(len(self.textMsgs) + 1), key='abcd', description='abcde',
                                      start_time='2018-06-03 13:00:00',
                                      end_time='2019-06-04 13:00:00',
                                      place='aaa', book_start='2018-06-03 13:00:00', book_end='2019-06-04 13:00:00',
                                      total_tickets=100, pic_url='http',
                                      remain_tickets=50, status=Activity.STATUS_PUBLISHED)
        msg = "退票 " + str(len(self.textMsgs) + 1)
        for user in users:
            if user.student_id:
                self.book_ticket(user, str(len(self.textMsgs) + 1))
            fromUser = user.open_id
            curTime = str(getTimeStamp(datetime.datetime.now()))
            msgId = str(random.randint(0, 99999)) + curTime
            data = getTextXml(fromUser, curTime, msg, msgId)

            # 剩余票数
            act = Activity.objects.filter(name=str(len(self.textMsgs) + 1)).first()
            remain_tickets_previous = act.remain_tickets

            response = self.client.post(
                path='/wechat/',
                content_type='application/xml',
                data=data
            )

            content = str(response.content.decode('utf-8'))
            if not user.student_id:
                self.assertEqual(self.is_unbind(content), True)
            else:
                self.assertEqual(self.refund_success(content), True)
                # 剩余票数
                act = Activity.objects.filter(name=str(len(self.textMsgs) + 1)).first()
                remain_tickets_current = act.remain_tickets
                self.assertEqual(remain_tickets_current, remain_tickets_previous + 1)
