from __future__ import absolute_import
from celery import Celery

app = Celery(
    'fnitter', 
    backend = 'redis://localhost', 
    broker = 'redis://localhost',
    include = ['Tasks.follow_accounts', 'Tasks.take_screenshot']
)
app.config_from_object('Driver.celeryconfig')

if __name__ == '__main__':
    app.start()
