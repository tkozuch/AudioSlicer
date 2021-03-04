# AudioSlicer

Audio Slicer is a web application for slicing audio files according to information given in form of text. 
A typical usage example includes slicing live concert record or album to individual songs. 
User gives only two information inputs: text informing about titles and cuts, and a file. 

An example input would being:
```
1. You Love Me - ye ye ye 0:00
2. My second song 3:40
3. I Love You 7:20
```

Will result in input file being sliced into 3 files:
```
"1. You Love me - ye ye ye.mp3" (00:00-3:40 of the input file)
"2. My second song.mp3" (3:40-7:20 of the input file)
"3. I love you.mp3" (7:20 -> the end of the input file)
```

During the process a real-time progress bar is displayed and the files are ready for download afterwards.

## Getting Started

### Prerequisites

-rabbitMQ

-python 3.6.3

-django 2.1.2

-celery 3.1.25

-pydub

### Start

Go to your local directory where you want the project to be stored and open GIT command line. 

Run command:
```
git clone https://github.com/tkozuch/AudioSlicer.git
```

### Installing requirements

Open terminal in project folder and run:

```
pip install -r requirements.txt
```

### Run celery worker

Go to AudioSlicer project folder and open terminal and:
```
celery -A audio_slicer worker -l info
```


### Start django app:

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

