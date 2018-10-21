web: cd file_upload && gunicorn file_upload.wsgi
worker: celery -A file_upload worker --loglevel=info