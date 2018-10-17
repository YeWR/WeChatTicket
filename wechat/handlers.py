# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity

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
        self.user.student_id = ''
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


class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        # 按照结束事件顺序排列
        activities = Activity.objects.filter(status=Activity.STATUS_PUBLISHED).order_by("end_time")
        if not activities:
            return self.reply_text(self.get_message('book_empty'))
        articles = []
        for act in activities:
            news = {}
            news['Title'] = '当前活动：' + act.name + '\n' \
                            + '剩余票数：' + str(act.remain_tickets) + '\n' \
                            + '抢票时间：' + str(act.start_time) + '-' + str(act.end_time)
            news['Description'] = act.description
            # news['Url'] =
            articles.append(news)
        return self.reply_news(articles)