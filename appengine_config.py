# -*- coding: utf-8 -*-
from google.appengine.ext import vendor
vendor.add('lib')

# pylint: disable=W0611,C0413
import requests
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()
