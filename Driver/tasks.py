from __future__ import absolute_import
from sys import stderr
from ConfigParser import SafeConfigParser as ConfigParser
import tweepy
from celery.utils.log import get_task_logger
from Driver.celery import app

l = get_task_logger(__name__)

class StreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        l.info('Received status: %s' % tweet)
        pass

    def on_error(self, status_code):
        l.error('Error: %s' % status_code)
        pass

    def on_data(self, jsonData):
        data = loads(jsonData)
        l.info('Tweet by %s: %s' % (data.get('name'), data.get('text'), ))
        pass

@app.task
def follow_accounts(account_list=[]):
    config = ConfigParser()
    config.read(['fnitter.cfg'])

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

@app.task
def take_screenshot(url, target_path):
    # Take a screenshot and save it
    from Driver.screenshot import Screenshot

    s = Screenshot(
        phantomjs_path = '/home/stemid/Development/fnitter/node_modules/phantomjs',
        url = url,
        output_dir = target_path
    )

    # I don't understand why PhantomJS had to remove process from Node, 
    # since it's a global part of Node.js but it's completely absent here. 
    # So I'm forced to use console.log and remove trailing newlines. 
    return { 'output': s._command_output.split('\n')[0] }
