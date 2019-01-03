# -*- coding: utf-8 -*-
import logging
from flask import Flask, render_template
from tumblr import act_stats, auto_reblog
from google.appengine.ext import deferred

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app = Flask(__name__)

@app.route("/")
def status():
    """Return status."""
    stats = act_stats(10)
    return render_template("status.html", title="tumblr status", stats=stats)

@app.route("/deffer")
def deffer_reblog():
    """Reblog task"""
    deferred.defer(auto_reblog)
    return "deffer"

@app.errorhandler(404)
def page_not_found(e): #pylint: disable=W0613
    """Return a custom 404 error."""
    return "Sorry, Nothing at this URL.", 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return "Sorry, unexpected error: {}".format(e), 500
