from __future__ import print_function, absolute_import
from importlib import import_module
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

# Helper function used by /tasks in REST API
def task_status(task_name=None):
    i = inspect()
    active_tasks = []
    active_tasks = i.active().get(
        'celery@%s' % config.get('fnitter', 'worker_name')
    )

    if task_name is None:
        if len(active_tasks):
            return active_tasks
        else:
            return False
    else:
        for task in active_tasks:
            if task.name == task_name and task.get('name', None) is not None:
                return [ task ]
    return False

# Get task status
@get('/tasks')
@get('/tasks/<task_name>')
@enable_cors
def get_tasks(task_name=None):
    response.content_type = 'application/json'
    try:
        status = task_status(task_name)
    except Exception as e:
        return {
            'status': 'Error',
            'message': str(e)
        }
    return status

# Start a task
@post('/tasks/<task_name>')
@enable_cors
def start_task(task_name=None):
    response.content_type = 'application/json'

    # Check unique param
    try:
        unique = request.query.getall('unique')[0]
    except Exception as e:
        print(str(e), file=stderr)
        unique = 'false'

    # Check if it's already running
    if unique == 'true':
        status = task_status(task_name)
        if status:
            return {
                'status': 'OK',
                'message': 'Task is already running'
            }

    # Import the task to run
    try:
        task = import_module(task_name)
    except Exception as e:
        return {
            'status': 'Error',
            'message': str(e)
        }

    # Run the task
    # TODO: Get arguments for task from GET params
    # TODO: Perhaps a list to act as tuple?

# Start celery task
@delete('/tasks/<task_name>')
@enable_cors
def stop_task():
    from Tasks.follow_accounts import follow_accounts
    response.content_type = 'application/json'

    accounts = []
    for (user_id, account_data) in db:
        accounts.append(str(user_id))

    # Check if task is already running, we don't want more than one of these.
    else:
        # If we have several running tasks, check for its name
        for task in active_tasks:
            # If found, return from the loop
            try:
                if task.name == 'Tasks.follow_accounts':
                    return {
                        'status': 'OK',
                        'message': 'Task is already running'
                    }
            except Exception as e:
                return {
                    'status': 'Error',
                    'message': str(e)
                }

    # If not found, start it
    try:
        follow_accounts.apply_async((accounts,))
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
