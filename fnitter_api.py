from __future__ import print_function
from sys import stderr
from ConfigParser import ConfigParser
from json import loads, dumps
from bottle import route, run, default_app, debug, response, request
from Driver.twitter import Twitter
from Driver.database import Database

config = ConfigParser()
config.read('fnitter.cfg')

twitter = Twitter(
    consumer_key = config.get('twitter', 'consumer_key'),
    consumer_secret = config.get('twitter', 'consumer_secret'),
    oauth_token = config.get('twitter', 'oauth_token'),
    oauth_secret = config.get('twitter', 'oauth_secret')
)

db = Database(config)

# Decorator to allow CORS
def enable_cors(fn):
    def _enable_cors(*args, **kw):
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        response.add_header('Access-Control-Allow-Origin', config.get('api', 'ui_url'))
        response.add_header('Access-Control-Allow-Methods', ', '.join(methods))
        #response.add_header('Access-Control-Allow-Headers', 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token')

        if request.method != 'OPTIONS':
            return fn(*args, **kw)
    return _enable_cors

@route('/accounts', method='GET')
@enable_cors
def accounts_get():
    response.content_type = 'application/json'

    response_list = []
    # Load JSON account data from DB for each user
    for (user_id, account_data) in db:
        response_list.append(loads(account_data))

    # Return JSON data in list form
    return dumps({'data': response_list})

@route('/account/<screen_name:re:[a-zA-Z0-9_]{,15}>', method='GET')
@enable_cors
def account_get(screen_name):
    response.content_type = 'application/json'
    # Get account info from DB
    user = twitter.api.get_user(name)

    return { 
        'user_id': user.id, 
        'screen_name': user.screen_name,
        'name': user.name,
        'friends': user.friends_count,
        'location': user.location,
        'time_zone': user.time_zone,
        'status_updates': user.statuses_count,
        'protected': user.protected,
        'description': user.description,
        'url': user.url
    }

@route('/account/<screen_name:re:[a-zA-Z0-9_]{,15}>', method='POST')
@enable_cors
def account_add(screen_name):
    response.content_type = 'application/json'
    # First verify this as a twitter screen name
    try:
        user = twitter.api.get_user(screen_name)
    except Exception as e:
        response.status = 404
        return {
            'status': 'Error',
            'message': str(e)
        }

    twitter_data = { 
        'user_id': user.id, 
        'screen_name': user.screen_name,
        'name': user.name,
        'friends': user.friends_count,
        'location': user.location,
        'time_zone': user.time_zone,
        'status_updates': user.statuses_count,
        'protected': user.protected,
        'description': user.description,
        'url': user.url
    }

    # Check if account exists in db
    for (user_id, account_data) in db:
        if user_id == twitter_data.get('user_id'):
            response.status = 409
            return {
                'status': 'Error',
                'message': 'Account exists'
            }

    try:
        db.add_account(
            twitter_data.get('user_id'),
            dumps(twitter_data)
        )
    except Exception as e:
        return {
            'status': 'Error',
            'message': str(e)
        }

    return { 
        'status': 'OK',
        'message': 'Account added'
    }

if __name__ == '__main__':
    run(
        host = config.get('api', 'host'), 
        port = config.get('api', 'port'),
        debug = True
    )
    debug(config.get('api', 'debug'))
else: # Assume WSGI
    application = default_app()
