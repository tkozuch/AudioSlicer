from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from . import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_slicer.settings')

try:
    redis = os.environ['REDIS_URL']
    app = Celery('audio_slicer', broker_pool_limit=1, broker=redis,
                 result_backend=redis, include=['slicing_app.slice_audio'])
except KeyError:
    app = Celery('audio_slicer', broker_pool_limit=1)

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
