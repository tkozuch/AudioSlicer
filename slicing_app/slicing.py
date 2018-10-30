from __future__ import absolute_import, unicode_literals
import re
import os
from django.template.defaultfilters import slugify
from pydub import AudioSegment
from celery import current_task, shared_task
from io import BytesIO
import boto3
from botocore.client import Config


@shared_task()
def slice_audio(s3_file_key, info_file):
    """ Slices album into individual songs, and saves them into new
    folder. Returns exact paths of the created songs. """
    file = download_s3_file(s3_file_key)
    audio = AudioSegment.from_mp3(file)
    #localization = get_localization(album_path)
    #album_name = album_path.split("/").pop()
    
    songs_info = extract_songs_info(info_file)
    songs_titles = list(songs_info.keys())
    number_of_songs = len(songs_titles)
    songs_times = list(songs_info.values())
    end_of_album = audio.duration_seconds
    songs_times.append(end_of_album)
    
    songs_paths = []
    #new_folder = create_song_folder(localization, album_name)
    files = []
    names = []
    urls = []
    for i in range(number_of_songs):
        song_title = songs_titles[i]
        file_name = slugify(song_title) + ".mp3"
        print("Extracting song titled: ", song_title)
        #total_song_path = "{}\\{}.mp3".format(new_folder, file_name)
        song = get_song_audio(i, audio, songs_times)
        percent = int(float(i) / float(number_of_songs) * 100)
        current_task.update_state(state='PROGRESS',
                                  meta={
                                      'current': i,
                                      'total': number_of_songs,
                                      'percent': percent
                                  })
        file = song.export(format="mp3", bitrate="202")
        #songs_paths.append(total_song_path)
        # Zwrocenie slownika tutaj z plikiem, czy zwrocenie obiektu pliku w
        # ogole tu powoduje wysypanie i blad typu 'cannot serialize'/ is not
        #  JSON serializable.
        # files[file_name]=file
        files.append(file)
        names.append(file_name)
        urls.append(upload_to_s3(file_name, file))
    
    return {'urls': urls, 'names': names}


def download_s3_file(key):
    s3_client = boto3.client('s3')
    s3_response_object = s3_client.get_object(Bucket='tikej', Key=key)
    object_content = s3_response_object['Body'].read()
    
    return BytesIO(object_content)


def upload_to_s3(key, file):
    """
    :return: list of url addresses of uploaded files.
    """
    
    ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    ACCESS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.environ.get('S3_BUCKET')
    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    s3.Bucket(BUCKET_NAME).put_object(Key=key, Body=file,
                                      ACL='public-read')
    url = "https://s3.eu-central-1.amazonaws.com/{}/{}".format(BUCKET_NAME,
                                                                key)
    
    return url


def extract_songs_info(file):
    songs_info = {}
    for line in file.split('\n'):
        # Time info indicate songs' starting times.
        # Valid time form is " 'one or more digits':'two digits' "
        # f.e. 03:40, 3:40, 73:40, 125:00. Thus the next line.
        match = re.search(r'\d+:\d\d', line)
        time = match.group(0)
        minute, second = time.split(':')
        time_in_seconds = int(minute) * 60 + int(second)
    
        song = line.replace(time, '').replace('.', '').replace('\n', '')
        songs_info[song] = time_in_seconds
    return songs_info


def create_song_folder(path, album_name):
    """ Creates folder for all the songs. """
    file_type_dot = album_name.rfind('.')
    folder_name = album_name[:file_type_dot]
    new_path = path + folder_name
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path


def get_song_audio(song_number, audio_segment, songs_times):
    """ Cuts out piece of audio from the album. """
    beginning = 1000 * songs_times[song_number]
    end = 1000 * songs_times[song_number + 1]
    return audio_segment[beginning:end]


def get_localization(path):
    """ Path of the folder containing the album. """
    last_slash = path.rfind('/')
    return path[:last_slash + 1]


#if __name__ == "__main__":
    # Only for testing purposes.
    #tkinter.Tk().withdraw()
    #print("Choose album.")
# albumPath = r"D:\Programowanie\PYTHON\Django\DivideAudio\test_files" \
#             r"\test_album.mp3"
# print("Choose information file.")
# #time_info = filedialog.askopenfile().name
# time_info = r"D:\Programowanie\PYTHON\Django\DivideAudio\test_files" \
#             r"\album_info.txt"
# if albumPath and time_info:
#     results = slice(albumPath, time_info)
#     print("Results {results}")
# else:
#     print("File(s) not chosen. Slicing aborted.")