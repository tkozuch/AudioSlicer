web: sh -c 'cd ./project/ && exec gunicorn project.audio_slicer.wsgi'
worker: sh -c 'cd ./project/ && exec celery -A audio_slicer worker --loglevel=debug
