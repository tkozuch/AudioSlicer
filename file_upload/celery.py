from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from . import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_upload.settings')

redis =  'redis://h:pfff9e307e0f39a1653556a4c6618924242d71829fb5b5df21314de128ff6a9a6@ec2-34-197-18-235.compute-1.amazonaws.com:64039'
app = Celery('file_upload', broker_pool_limit=1, broker=redis,
             result_backend=redis)

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))