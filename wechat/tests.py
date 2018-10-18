from django.test import TestCase, Client
from django.contrib.auth.models import User
from wechat.models import Activity
from django.utils import timezone
from django.contrib.auth import authenticate, logout, login
from . import views as views
# import requests
import json
import logging
import time
import datetime

c = Client(HTTP_USER_AGENT='Mozilla/5.0')


class TestError(TestCase):
    pass


class TestDefault(TestCase):
    pass


class TestHelpOrSubscribe(TestCase):
    pass


class TestUnbindOrUnsubscribe(TestCase):
    pass


class TestBindAccount(TestCase):
    pass


class TestBookEmpty(TestCase):
    pass


class TestBookWhat(TestCase):
    pass


class TestCheckTicket(TestCase):
    pass


class TestBookTicket(TestCase):
    pass


class TestRefundTicket(TestCase):
    pass
