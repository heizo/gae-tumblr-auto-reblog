# gae-tumblr-auto-reblog

## About
[GAE/Python] Tumblr periodic reblog bot.
Reblogging from past posts at random and add to queue if the queue has decreased.
My tumblr blog(https://oninoheizo.tumblr.com) is managed by this program.

## Requirements
- [Google Cloud SDK for Python][]
- [Tumblr][]
- [pytumblr][]
- [flask][]

### pip install
```bash
$ cd /your/project
$ pip install -t lib flask pytumblr python-dateutil pytz requests-toolbelt
```

### OAUTH secret keys
```bash
$ cp secret.yaml.sample secret.yaml
```
secret.yaml
```yaml
env_variables:
  BLOG_NAME: "YOUR BLOG NAME"
  CONSUMER_KEY: "YOUR CONSUMER KEY"
  CONSUMER_SECRET: "YOUR CONSUMER SECRET"
  OAUTH_TOKEN: "YOUR OAUTH TOKEN"
  OAUTH_SECRET: "YOUR OAUTH SECRET"
```
Add your blog name, consumer_key, consumer_secret, oauth_token and oauth_secret.  
https://www.tumblr.com/oauth/apps  
https://github.com/stigok/node-oauth-tumblr-example

## Configuration
### Google App Engine
- Create a project.
### tumblr
- Enable automatically publish a queued post.  
(e.g. 5 times a day between 12 am and 12 am)
### settings.py
- MIN_QUEUE: Run reblog task if the number of queues is less than MIN_QUEUE.
- ADD_QUEUE: Number of posts in a single reblog task.
- DAYS_BEFORE: Reblog posts are older than DAYS_BEFORE days from now.
- MIN_NOTE: Reblog posts have more than MIN_NOTE notes.
### cron.yaml
```yaml
cron:
- description: "update check"
  url: /deffer
  schedule: every 3 hours
```
check the queue every 3 hours.

## Deploy
```bash
$ gcloud app deploy
$ gcloud app deploy cron.yaml
$ gcloud app deploy queue.yaml
```

## Issues
Need a lot of past posts.

## Reblog forever!

[Tumblr]: https://www.tumblr.com/
[Google Cloud SDK for Python]: https://cloud.google.com/appengine/docs/standard/python/download
[pytumblr]: https://github.com/tumblr/pytumblr
[flask]: http://flask.pocoo.org/


