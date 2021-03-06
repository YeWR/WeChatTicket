# -*- coding: utf-8 -*-
#
import datetime
import time
import uuid

from django.db.models import Q,F
from django.db import transaction

from wechat.models import Activity, Ticket
from wechat.wrapper import WeChatHandler

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        if not self.user or not self.user.student_id:
            return self.reply_text('对不起，您还没有绑定，不能解绑。')
        else:
            self.user.student_id = None
            self.user.save()
            return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        if self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))
        else:
            return self.reply_single_news({
                'Title': "绑定学号",
                'Description': "请点击下方链接进行学号绑定",
                'Url': self.url_bind(),
            })


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


# 抢啥
class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        # 按照结束事件顺序排列
        activities = Activity.objects.filter(status=Activity.STATUS_PUBLISHED).order_by("end_time")
        if not activities:
            return self.reply_text(self.get_message('book_empty'))
        articles = []
        for act in activities.iterator():
            article = {}
            article['Title'] = '当前活动：' + act.name + '\n' \
                               + '剩余票数：' + str(act.remain_tickets) + '\n' \
                               + '抢票时间：' + str(act.start_time) + '-' + str(act.end_time)
            article['Description'] = act.description
            article['Url'] = self.url_book_what(act.id)
            article['PicUrl'] = act.pic_url
            articles.append(article)
        return self.reply_news(articles)


#  查票
class CheckTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_in('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        # 判断是否有效
        if not self.user or not self.user.student_id:
            return self.reply_single_news({
                'Title': "绑定学号",
                'Description': "请点击下方链接进行学号绑定",
                'Url': self.url_bind(),
            })
        else:
            # flag 1-> 查票
            flag = 0
            activity = None
            # 如果输入查票
            if self.is_text_in('查票'):
                # >>> 查票 XXXX
                query = self.input['Content'][3:]
                if not query:
                    flag = 0
                else:
                    activity = Activity.objects.filter(name=query)
                    if activity:
                        flag = 1
            # 点击抢票
            elif self.is_event_click(self.view.event_keys['get_ticket']):
                flag = 1

            if flag == 0:
                return self.reply_text('亲~您没有此活动的票或此活动的不存在哟~')

            # 查票
            # 查所有的票
            if not activity:
                tickets = Ticket.objects.filter(student_id=self.user.student_id, status=Ticket.STATUS_VALID).select_related('activity')
            else:
                tickets = Ticket.objects.filter(student_id=self.user.student_id, status=Ticket.STATUS_VALID, activity=activity).select_related('activity')

            if not tickets:
                return self.reply_text('亲~您没有此活动的票或此活动的不存在哟~')

            reses = []
            for ticket in tickets.iterator():
                act = ticket.activity
                res = {}
                res['Title'] = '您的活动：' + act.name
                res['Description'] = '活动地点：' + act.place + '\n' \
                                     + '活动开始时间：' + str(act.start_time.timestamp()) + '活动结束时间' + str(act.end_time.timestamp())
                res['Url'] = self.url_book_ticket(ticket.unique_id)
                res['PicUrl'] = act.pic_url
                reses.append(res)
            return self.reply_news(reses)


# 抢票
class BookTicketHandler(WeChatHandler):

    def getTimeStamp(self, timeObj):
        return int(time.mktime(timeObj.timetuple()))

    def getUniqueId(self):
        u3 = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.user.student_id)).replace('-', 'x')
        u4 = str(uuid.uuid4()).replace('-', 'o')
        u = u4[5:15] + u3
        return u

    def check(self):
        return self.is_text_in('抢票') or self.is_event_book_click(self.view.event_keys['book_header'])

    def handle(self):
        # 判断是否有效
        if not self.user or not self.user.student_id:
            return self.reply_single_news({
                'Title': "绑定学号",
                'Description': "请点击下方链接进行学号绑定",
                'Url': self.url_bind(),
            })
        else:
            # activity
            activity = None
            # 当前时间戳
            currentTime = self.getTimeStamp(datetime.datetime.now())
            # 是否是text输入
            text_flag = True
            text_flag_val = None

            # 如果输入抢票
            if self.is_text_in('抢票'):
                # >>> 抢票 XXXX
                query = self.input['Content'][3:]
                text_flag_val = query
                activity = Activity.objects.filter(name=query).first()
            # 点击抢票
            elif self.is_event_book_click(self.view.event_keys['book_header']):
                text_flag = False
                id = int(self.input['EventKey'].split('_')[-1])
                text_flag_val = id
                activity = Activity.objects.filter(id=id).first()

            # 没有该活动
            if not activity:
                return self.reply_text('对不起，不存在该活动！')
            # 活动取消
            elif activity.status == Activity.STATUS_DELETED:
                return self.reply_text('对不起，该活动已取消！')
            # 活动未发布
            elif activity.status == Activity.STATUS_SAVED:
                return self.reply_text('对不起，该活动还未发布！')
            # 抢票没开始
            elif currentTime < self.getTimeStamp(activity.book_start):
                return self.reply_text('对不起，抢票尚未开始！')
            # 抢票结束
            elif currentTime >= self.getTimeStamp(activity.book_end):
                return self.reply_text('对不起，抢票已结束！')
            # 没有票了
            elif activity.remain_tickets <= 0:
                return self.reply_text('对不起，票已售空！')

            # 是否已有票
            yourTicket = Ticket.objects.filter(student_id=self.user.student_id, activity=activity).first()

            # 已有票
            if yourTicket and yourTicket.status == Ticket.STATUS_VALID:
                return self.reply_text('对不起，您已购过票！')
            # 已使用过票
            elif yourTicket and yourTicket.status == Ticket.STATUS_USED:
                return self.reply_text('对不起，您已使用过票！')
            # 退票重购票
            elif yourTicket and yourTicket.status == Ticket.STATUS_CANCELLED:
                # 加锁
                with transaction.atomic():
                    if text_flag:
                        activity = Activity.objects.select_for_update().filter(name=text_flag_val).first()
                    else:
                        activity = Activity.objects.select_for_update().filter(id=text_flag_val).first()

                    if activity.remain_tickets <= 0:
                        return self.reply_text('对不起，票已售空！')

                    yourTicket = Ticket.objects.select_for_update().filter(student_id=self.user.student_id,
                                                                           activity=activity).first()
                    yourTicket.status = Ticket.STATUS_VALID
                    yourTicket.save()

                    activity.remain_tickets -= 1
                    activity.save()

                return self.reply_single_news({
                    'Title': self.user.student_id + '，您好！' + activity.name + "已抢票成功！（重购此票）",
                    'Description': activity.description,
                    'Url': self.url_book_ticket(yourTicket.unique_id),
                    'PicUrl': activity.pic_url,
                })
            # 购买新票
            else:
                # 加锁

                with transaction.atomic():
                    if text_flag:
                        activity = Activity.objects.select_for_update().filter(name=text_flag_val).first()
                    else:
                        activity = Activity.objects.select_for_update().filter(id=text_flag_val).first()

                    if activity.remain_tickets <= 0:
                        return self.reply_text('对不起，票已售空！')

                    newTicket = Ticket.objects.select_for_update().create(
                        student_id=self.user.student_id,
                        unique_id=self.getUniqueId(),
                        activity=activity,
                        status=Ticket.STATUS_VALID
                    )
                    # 剩余票数减少
                    activity.remain_tickets -= 1
                    activity.save()

                return self.reply_single_news({
                    'Title': self.user.student_id + '，您好！' + activity.name + "已抢票成功！（新票）",
                    'Description': activity.description,
                    'Url': self.url_book_ticket(newTicket.unique_id),
                    'PicUrl': activity.pic_url,
                })


class RefundTicketHandler(WeChatHandler):

    def getTimeStamp(self, timeObj):
        return int(time.mktime(timeObj.timetuple()))

    def check(self):
        return self.is_text_in('退票')

    def handle(self):
        # 判断是否有效
        if not self.user or not self.user.student_id:
            return self.reply_single_news({
                'Title': "绑定学号",
                'Description': "请点击下方链接进行学号绑定",
                'Url': self.url_bind(),
            })
        else:
            # >>> 退票 XXXX
            query = self.input['Content'][3:]
            activity = Activity.objects.filter(name=query).first()

            # 当前时间戳
            currentTime = self.getTimeStamp(datetime.datetime.now())

            # 没有该活动
            if not activity:
                return self.reply_text('对不起，不存在该活动，无法退票！')
            # 活动取消
            elif activity.status == Activity.STATUS_DELETED:
                return self.reply_text('对不起，该活动已取消，无法退票！')
            # 活动未发布
            elif activity.status == Activity.STATUS_SAVED:
                return self.reply_text('对不起，该活动还未发布，无法退票！')
            # 抢票没开始
            elif currentTime < self.getTimeStamp(activity.book_start):
                return self.reply_text('对不起，抢票尚未开始，无法退票！')
            # 抢票结束
            elif currentTime >= self.getTimeStamp(activity.book_end):
                return self.reply_text('对不起，抢票已结束，无法退票！')

            # 用户的票
            yourTicket = Ticket.objects.filter(student_id=self.user.student_id,
                                               activity=activity).first()
            # 尚未购票
            if not yourTicket:
                return self.reply_text('对不起，您尚未购票，无法退票！')
            elif yourTicket.status == Ticket.STATUS_CANCELLED:
                return self.reply_text('对不起，您已退过此票，无法退票！')
            elif yourTicket.status == Ticket.STATUS_USED:
                return self.reply_text('对不起，您已使用过此票，无法退票！')

            # 加锁
            with transaction.atomic():
                activity = Activity.objects.select_for_update().filter(name=query).first()
                yourTicket = Ticket.objects.select_for_update().filter(student_id=self.user.student_id,
                                                                       activity=activity).update(status=Ticket.STATUS_CANCELLED)

                # 退票成功
                #yourTicket.status = Ticket.STATUS_CANCELLED
                #yourTicket.save()

                # 票数增加
                activity.remain_tickets += 1
                activity.save()

            return self.reply_text('您已成功退票！')
