from __future__ import absolute_import
from json import loads
from ConfigParser import SafeConfigParser as ConfigParser
import tweepy
from Driver.celery import app
from celery.utils.log import get_task_logger
from Tasks.take_screenshot import take_screenshot

l = get_task_logger(__name__)

config = ConfigParser()
config.read(['fnitter.cfg'])

class StreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        l.info('Received status: %s' % tweet)

    def on_error(self, status_code):
        l.error('Error: %s' % status_code)

    def on_data(self, jsonData):
        data = loads(jsonData)
        if data.has_key('delete'):
            l.info('tweet deleted')
            return { 'status': 'Tweet deleted' }
        else:
            text = data.get('text')
            user = data.get('user')
            user_id = user.get('id')
            screen_name = user.get('screen_name')

        try:
            screenshot = take_screenshot.apply_async((
                user_id,
                'https://twitter.com/'+screen_name
            ))
        except Exception as e:
            l.error('take_screenshot task failed: %s' % str(e))

@app.task
def follow_accounts(account_list=[]):
    consumer_key = config.get('fnitter', 'consumer_key')
    consumer_secret = config.get('fnitter', 'consumer_secret')
    oauth_token = config.get('fnitter', 'oauth_token')
    oauth_secret = config.get('fnitter', 'oauth_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(oauth_token, oauth_secret)

    listener = StreamListener()

    stream = tweepy.Stream(auth=auth, listener=listener)
    stream.filter(follow = account_list)

    # return stream status when it ends
    return stream.running
