# AudioSlicer

Audio Slicer is a web application for slicing audio files according to information given in form of text. A typical usage example includes slicing live concert record or album to individual songs. User gives only two input informations: text informing about titles and cuts, and a file.

An example text would be:
```
1. You Love Me - ye ye ye 0:00
2. My second song 3:40
3. I Love You 7:20
```

Where time indicates songs' starting times.

## Getting Started

Go to your local directory where you want the project to be stored and open GIT command line. 

Run command:
```
git clone https://github.com/tkozuch/AudioSlicer.git
```
Go to AudioSlicer project folder and open terminal and:
```
celery -A file_upload worker -l info
```

Open another terminal and:

```
python manage.py runserver
```

Now website is available on local address: http://127.0.0.1:8000/

### Prerequisites

-rabbitMQ

-python 3.6.3

-django 2.1.2

-celery 3.1.25

-pydub


### Installing requirements

Open terminal in project folder and run:

```
pip install -r requirements.txt
```

## Built With
-Django framework
-Bootstrap
-Jquery
-Celery

## Author

Tomasz Kożuch

## License

The author takes no legal responsibility for any out of law use of this application.
Redistributing this project without knowledge and permission from the author is forbidden. However I allow for personal non-commercial use.

