# AudioSlicer

Audio Slicer is a web application for slicing audio files according to information given in 
form of text.

## Demo

Demo of application is available on https://audio-slicer.herokuapp.com/ 

(Due to Heroku's 30s max request time policy, the above demo may work only on small files. 
Was tested there on a test file of size ~500kB: `AudioSlicer/slicing_app/tests/test_ablum_shorter
.mp3`.)

## Usage example

An example input (inserted in the UI):
```
title:                          time:
1. You Love Me - ye ye ye       0:00
2. My second song               3:40
3. I Love You                   7:20
```

This will result in input file being sliced into 3 files:
```
"1. You Love me - ye ye ye.mp3"   (00:00-3:40 of the input file)
"2. My second song.mp3"           (3:40-7:20 of the input file)
"3. I love you.mp3"               (7:20 -> the end of the input file)
```

During the process a real-time progress bar is displayed and the files are ready for download afterwards.

## Getting Started

### Prerequisites:

Get repository:

`git clone https://github.com/tkozuch/AudioSlicer.git`

Past .env file:
(For the project to fully work you will need to ask developer about `.env` file with environmental variables.)

When acquired place the file in project folder (`AudioSlicer`)

All required ENV_VARIABLES:
```
S3_BUCKET
SECRET_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
CELERY_BROKER_URL
CELERY_RESULT_BACKEND
PYTHONUNBUFFERED
DISABLE_COLLECTSTATIC
C_FORCE_ROOT
RUNNING_ON_HEROKU
DEBUG
```

## Start with docker:

Having Docker installed on your computer, go into project folder and execute:
<br>`docker-compose build`
<br>`docker-compose up`

Wait after requirements are downloaded, built and up-and-running.
 
(After build, starting of application should take around 1 minute. Usually the process is  finished
 when the logging to console stops with `[...]celery@xxx ready.` message.)

Visit http://127.0.0.1:8000/ to check the application.


## Start by hand

#### Requirements
-rabbitMQ

-python 3.6.3

#### Installing python requirements

(Optional) Make and activate virtual environment:

`python -m venv ./.venv`

Activate on Windows:
<br>`.\.venv\Scripts\activate`
<br>Activate on Linux-Ubuntu:
<br>`source ./bin/activate`

Open terminal in project folder and run:

```
pip install -r requirements.txt
```

#### Set environmental variables:

With bash: `source ./set_env.sh`<br>
Windows Powershell/command prompt: you're on your own.

#### Run celery worker

Go to AudioSlicer project folder, open terminal and:
```
celery -A audio_slicer worker -l info
```


#### Start django app:

Open another terminal (celery worker needs to be running) and:

```
python manage.py runserver
```

Now website is available on local address: http://127.0.0.1:8000/


#### To run tests:

`python manage.py test slicing_app.tests`

## Built With
-Django framework
-Bootstrap
-Jquery
-Celery

## Author

Tomasz Kożuch

## License

The author takes no legal responsibility for any out of law use of this application.
Redistributing this project without knowledge and permission from the author is forbidden. However personal, non-commercial use is allowed.
