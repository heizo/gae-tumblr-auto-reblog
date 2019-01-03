# -*- coding: utf-8 -*-
import os

BLOG_NAME = os.environ.get('BLOG_NAME')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
OAUTH_TOKEN = os.environ.get('OAUTH_TOKEN')
OAUTH_SECRET = os.environ.get('OAUTH_SECRET')

MAX_QUEUE = 300
MIN_QUEUE = 50
DAYS_BEFORE = 90
MIN_NOTE = 2
ADD_QUEUE = 30
