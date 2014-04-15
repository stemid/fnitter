from __future__ import print_function, absolute_import
from sys import stderr
from ConfigParser import SafeConfigParser as ConfigParser
from json import loads, dumps, JSONEncoder
from bottle import post, get, run, default_app, debug, response, request
from celery.task.control import inspect
from Driver.twitter import Twitter
from Driver.database import Database
from Driver.celery import app

config = ConfigParser()
config.read('fnitter.cfg')

twitter = Twitter(
    consumer_key = config.get('fnitter', 'consumer_key'),
    consumer_secret = config.get('fnitter', 'consumer_secret'),
    oauth_token = config.get('fnitter', 'oauth_token'),
    oauth_secret = config.get('fnitter', 'oauth_secret')
)

db = Database(config)

# Converting datetime objects for JSON
class DateEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)

# Decorator to allow CORS
def enable_cors(fn):
    def _enable_cors(*args, **kw):
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        response.add_header(
            'Access-Control-Allow-Origin', 
            config.get('fnitter', 'ui_url')
        )
        response.add_header(
            'Access-Control-Allow-Methods', 
            ', '.join(methods)
        )
        #response.add_header('Access-Control-Allow-Headers', 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token')

        if request.method != 'OPTIONS':
            return fn(*args, **kw)
    return _enable_cors

@get('/accounts')
@enable_cors
def accounts_get():
    response.content_type = 'application/json'

    response_list = []
    # Load JSON account data from DB for each user
    for (user_id, account_data) in db:
        response_list.append(loads(account_data))

    # Return JSON data in list form
    return dumps({'data': response_list})

@get('/account/<screen_name:re:[a-zA-Z0-9_]{,15}>')
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

@post('/account/<screen_name:re:[a-zA-Z0-9_]{,15}>')
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
        response.status = 500
        return {
            'status': 'Error',
            'message': str(e)
        }

    return { 
        'status': 'OK',
        'message': 'Account added'
    }

# Get all celery tasks in a list
# Get status of a celery task
@get('/task')
@get('/task/<task_name>')
@enable_cors
def get_task(task_name=None):
    response.content_type = 'application/json'

    i = inspect()
    active_tasks = []
    try:
        active_tasks = i.active().get(
            'celery@%s' % config.get('fnitter', 'worker_name')
        )
    except Exception as e:
        response.status = 500
        return {
            'status': 'Error',
            'message': str(e)
        }

    if not len(active_tasks):
        response.status = 404
        return {
            'status': 'Not found',
            'message': 'No tasks are running'
        }

    if task_name is None:
        return { 
            'status': 'OK', 
            'tasks': active_tasks 
        }

    for task in active_tasks:
        if task_name == task.get('name'):
            return { 
                'status': 'OK',
                'tasks': [ task ] 
            }

    return {
        'status': 'Not found',
        'message': 'Task not found'
    }

# Helper function to actually start the task
def task_follow_accounts(account_list):
    from Tasks.follow_accounts import follow_accounts
    follow_accounts.apply_async((account_list,))

# Start celery task
@post('/task/follow_accounts')
@enable_cors
def start_follow_accounts():
    response.content_type = 'application/json'

    accounts = []
    for (user_id, account_data) in db:
        accounts.append(user_id)

    # Check if task is already running, we don't want more than one of these.
    # Get current list of active tasks
    active_tasks = []
    try:
        active_tasks = i.active().get(
            'celery@%s' % config.get('fnitter', 'worker_name')
        )
    except Exception as e:
        response.status = 500
        return {
            'status': 'Error',
            'message': str(e)
        }

    if not len(active_tasks):
        task_follow_accounts()
        return {
            'status': 'OK',
            'message': 'Task started'
        }

    # If we have several running tasks, check for its name
    for task in active_tasks:
        # If found, return from the loop
        if task.name == 'Driver.tasks.follow_accounts':
            return {
                'status': 'OK',
                'message': 'Task is already running'
            }

    # If not found, start it
    try:
        task_follow_accounts()
    except Exception as e:
        return {
            'status': 'Error',
            'message': str(e)
        }

    return {
        'status': 'OK',
        'message': 'Task started'
    }

if __name__ == '__main__':
    run(
        host = config.get('fnitter', 'host'), 
        port = config.get('fnitter', 'port'),
        debug = True
    )
    debug(config.get('fnitter', 'debug'))
else: # Assume WSGI
    application = default_app()
