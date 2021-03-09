# AudioSlicer

Audio Slicer is a web application for slicing audio files according to information given in form of text.

## Demo

Demo of application is available on https://audio-slicer.herokuapp.com/ 

(Due to Heroku's 30s max request time policy, the above demo may work only on small files. Was tested there on a test file
 - AudioSlicer/slicing_app/tests/test_ablum_shorter.mp3.)

## Usage example

A typical usage example includes slicing live concert record or album to individual songs. 
User gives only two information inputs: text informing about titles and cuts, and a file. 

An example:
```
1. You Love Me - ye ye ye 0:00
2. My second song 3:40
3. I Love You 7:20
```

This will result in input file being sliced into 3 files:
```
"1. You Love me - ye ye ye.mp3" (00:00-3:40 of the input file)
"2. My second song.mp3" (3:40-7:20 of the input file)
"3. I love you.mp3" (7:20 -> the end of the input file)
```

During the process a real-time progress bar is displayed and the files are ready for download afterwards.

## Getting Started

## Starting with docker
For the project to fully work you will need to ask developer about `.env` file with environmental variables.

Having Docker installed on your computer, go into project folder and execute:
<br>`docker-compose build`
<br>`docker-compose up`

Wait after requirements are downloaded, built and up-and-running.

The application will be available at http://127.0.0.1:8000/

## Starting by hand

#### Requirements
-rabbitMQ

-python 3.6.3

-django 2.1.2

-celery 3.1.25

-pydub

#### Start

Go to your local directory where you want the project to be stored and open GIT command line. 

Run command:
```
git clone https://github.com/tkozuch/AudioSlicer.git
```

#### Installing python requirements

Open terminal in project folder and run:

```
pip install -r requirements.txt
```

#### Run celery worker

Go to AudioSlicer project folder, open terminal and:
```
celery -A audio_slicer worker -l info
```


#### Start django app:

Open another terminal and:

```
python manage.py runserver
```

Now website is available on local address: http://127.0.0.1:8000/


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
