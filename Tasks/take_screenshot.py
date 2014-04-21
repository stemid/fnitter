from __future__ import absolute_import
from os import mkdir
from json import dumps
from ConfigParser import SafeConfigParser as ConfigParser
from celery.utils.log import get_task_logger
from Driver.celery import app
from Driver.screenshot import Screenshot
from Driver.database import Database

l = get_task_logger(__name__)

config = ConfigParser()
config.read(['fnitter.cfg'])

db = Database(config)

@app.task
def take_screenshot(user_id, url):
    l.info('Taking screenshot of %s' % url)
    output_dir = '%s/%s' % (
        config.get('fnitter', 'media_path'),
        user_id
    )

    # First make sure output_dir path exists
    try:
        mkdir(output_dir, 0755)
    except:
        pass

    # Take a screenshot and save it
    s = Screenshot(
        phantomjs_path = '/home/stemid/Development/fnitter/node_modules/phantomjs',
        url = url,
        output_dir = output_dir
    )

    # I don't understand why PhantomJS had to remove process from Node, 
    # since it's a global part of Node.js but it's completely absent here. 
    # So I'm forced to use console.log in JS and remove trailing newlines. 
    cmd_output = s._command_output.split('\n')[0]
    l.info('Captured screenshot %s' % cmd_output)

    screenshot_data = {
        'filename': cmd_output,
        'filepath': '%s/%s' % (
            output_dir,
            cmd_output
        ),
        'url': '%s/%s/%s' % (
            config.get('fnitter', 'media_url'),
            user_id,
            cmd_output
        )
    }

    try:
        db.log_screenshot(user_id, dumps(screenshot_data))
    except Exception as e:
        l.error('db.log_screenshot exception: %s' % str(e))
        return { 'status': 'Exception: %s' % str(e) }

    return { 'status': 'Screenshot saved' }
