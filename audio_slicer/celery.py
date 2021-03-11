from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from . import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audio_slicer.settings")


CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"

app = Celery(
    "audio_slicer",
    broker_pool_limit=1,
    backend=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    accept_content=CELERY_ACCEPT_CONTENT,
    task_serializer=CELERY_TASK_SERIALIZER,
    result_serializer=CELERY_RESULT_SERIALIZER
)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
