# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from random import randrange
from time import time
from google.appengine.ext import ndb
import dateutil.parser
import pytz
import pytumblr
import settings

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Activity(ndb.Model):
    name = ndb.StringProperty(required=True)
    queue = ndb.IntegerProperty(required=True)
    followers = ndb.IntegerProperty(required=True)
    posts = ndb.IntegerProperty(required=True)
    reblogs = ndb.IntegerProperty()
    exectime = ndb.FloatProperty()
    updated_at = ndb.DateTimeProperty(auto_now_add=True)

def act_stats(num):
    return Activity.query().order(-Activity.updated_at).fetch(num)

def act_save(name, queue, followers, posts, reblogs, exectime):
    act = Activity(
        name=name,
        queue=queue,
        followers=followers,
        posts=posts,
        reblogs=reblogs,
        exectime=exectime
    )
    act.put()


class Reblog(ndb.Model):
    offset = ndb.IntegerProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)
    post_date = ndb.StringProperty(required=True)
    post_url = ndb.StringProperty(required=True)
    source_url = ndb.StringProperty()
    reblogged_to = ndb.StringProperty(required=True)
    reblogged_date = ndb.StringProperty(required=True)
    note_count = ndb.IntegerProperty(required=True)
    updated_at = ndb.DateTimeProperty(auto_now_add=True)

def reblog_save(offset, post_id, post_date, post_url, source_url,
                reblogged_to, reblogged_date, note_count):
    rb = Reblog(
        offset=offset,
        post_id=post_id,
        post_date=post_date,
        post_url=post_url,
        source_url=source_url,
        reblogged_to=reblogged_to,
        reblogged_date=reblogged_date,
        note_count=note_count
    )
    rb.put()

def reblog_list(num):
    return Reblog.query().order(-Reblog.updated_at).fetch(num)

def _client():
    return pytumblr.TumblrRestClient(
        settings.CONSUMER_KEY,
        settings.CONSUMER_SECRET,
        settings.OAUTH_TOKEN,
        settings.OAUTH_SECRET
    )

def _bloginfo(client, blogname):
    try:
        info = client.blog_info(blogname)
    except Exception as e: #pylint: disable=W0703
        logger.error("%s", e.args)
        return
    if "blog" not in info:
        logger.error("blog not found blogname=%s", blogname)
        return
    return info["blog"]

def bloginfo():
    return _bloginfo(_client(), settings.BLOG_NAME)


def get_post(client, blogname, post_id=None, offset=0, reblog_info=False, notes_info=False):
    res = client.posts(blogname, id=post_id, offset=offset, limit=1,
                       reblog_info=reblog_info, notes_info=notes_info)
    if res is None or "posts" not in res or not res["posts"]:
        logger.error("post not found bloname=%s, id=%s", blogname, post_id)
        return
    return res["posts"][0]

def random_post(client, blogname, maxposts, limday, min_note):
    MAX_TRIES = 7
    for _ in range(MAX_TRIES):
        offset = randrange(maxposts)
        post = get_post(client, blogname, offset=offset, reblog_info=True, notes_info=True)
        if post is None:
            continue
        if post["state"] != "published":
            continue
        if post["note_count"] < min_note:
            continue
        if dateutil.parser.parse(post["date"]) > limday:
            continue
        return post, offset

def reblog_filter(post, myname=None):
    notes = post.get("notes")
    if not notes:
        return
    res = []
    for note in notes:
        if (note["type"] == "reblog" and note["blog_name"] != myname
                and note["reblog_parent_blog_name"] != myname):
            res.append(note)
    return max(res, key=lambda x: x["timestamp"]) if res else None


def random_reblog(blogname, num, before, min_note):
    client = _client()
    info = _bloginfo(client, blogname)
    if info is None:
        return
    if info["queue"] >= settings.MIN_QUEUE:
        logger.debug("queue %d >= MIN_QUEUE[%d]", info["queue"], settings.MIN_QUEUE)
        info["reblogs"] = 0
        return info
    blogname = info["name"]
    maxposts = info["posts"]
    limday = datetime.now(pytz.utc) - timedelta(days=before)
    if info["queue"] + num > settings.MAX_QUEUE:
        num = settings.MAX_QUEUE - info["queue"]
    offsets = []
    for i in range(num * 2):
        post, offset = random_post(client, blogname, maxposts, limday, min_note)
        if post is None or offset in offsets:
            logger.debug("[%d] - NG", i)
            continue
        rb = reblog_filter(post, myname=blogname)
        if not rb:
            logger.debug("[%d] - No notes", i)
            continue
        reblog = get_post(client, rb["blog_name"], post_id=rb["post_id"])
        if reblog is None:
            continue
        offsets.append(offset)
        logger.debug("[%d] - OK", i)
        logger.debug("POST=%s, id=%s", post["date"], post["id"])
        logger.debug(" ==> %s, '%s', notes=%d",
                     reblog["date"], reblog["blog_name"], reblog["note_count"])
        client.reblog(blogname, id=reblog["id"], reblog_key=reblog["reblog_key"], state="queue")
        reblog_save(
            offset=offset,
            post_id=post["id"],
            post_date=post["date"],
            post_url=post["post_url"],
            source_url=post["source_url"] if "source_url" in post else "",
            reblogged_to=reblog["blog_name"],
            reblogged_date=reblog["date"],
            note_count=reblog["note_count"])
        if len(offsets) >= num:
            break
    else:
        logger.error("exceeds maximum limits: %d", i)
    info["reblogs"] = len(offsets)
    logger.info("reblog! [%d]", info["reblogs"])
    return info

def auto_reblog(num=settings.ADD_QUEUE):
    t1 = time()
    info = random_reblog(
        blogname=settings.BLOG_NAME,
        num=num,
        before=settings.DAYS_BEFORE,
        min_note=settings.MIN_NOTE)
    t2 = time()
    logger.info("elapsed_time: %.2f [sec]", t2 - t1)
    if info is not None:
        act_save(info["name"], info["queue"], info["followers"], info["posts"],
                 info["reblogs"], t2 - t1)
    return info
