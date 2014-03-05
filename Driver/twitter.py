import tweepy

class Twitter:
    def __init__(self, **options):
        consumer_key = options.get('consumer_key')
        consumer_secret = options.get('consumer_secret')
        oauth_token = options.get('oauth_token')
        oauth_secret = options.get('oauth_secret')

        self._auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self._auth.set_access_token(oauth_token, oauth_secret)

        self.api = tweepy.API(self._auth)
