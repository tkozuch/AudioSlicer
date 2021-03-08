import os
import re
from logging import getLogger

import boto3
from botocore.client import Config
from celery import current_task, shared_task
from django.template.defaultfilters import slugify
from pydub import AudioSegment

TIME_FORMAT = r'\d\d:\d\d:\d\d'

log = getLogger(__file__)


@shared_task()
def slice_audio(file, text_input, upload=False):
    """
    Slices audio file according to information given in text input.
    """

    if not (
            (getattr(file, 'read', False) or isinstance(file, str)) and
            isinstance(text_input, str) and
            isinstance(upload, bool)
    ):
        raise AttributeError
    
    def get_song_audio(song_number, audio_segment, songs_times):
        """
        Cuts out piece of audio from the audio file.
        """
        
        beginning = 1000 * songs_times[song_number]
        end = 1000 * songs_times[song_number + 1]
    
        return audio_segment[beginning:end]

    def upload_to_s3(key, file):
        """
        Uploads to Amazon S3 service.
        :return: string
        """
        
        access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        access_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.environ.get('S3_BUCKET')
        s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_secret_key,
            config=Config(signature_version='s3v4')
        )
        log.info(f"Uploading to S3: {key} | {file}")
        s3.Bucket(bucket_name).put_object(
            Key=key,
            Body=file,
            ACL='public-read'
        )
        url = "https://s3.eu-central-1.amazonaws.com/{}/{}".format(
            bucket_name,
            key
        )

        return url
    
    try:
        audio = AudioSegment.from_mp3(file)
    except Exception as exc:  # TODO: Add custom exception.
        log.exception(f"Problem loading audio: \n{exc}")
        raise ValueError(exc)
    else:
        log.info("Successfuly loaded audio")

    audio_info = extract_songs_info(text_input)

    slicing_titles = list(audio_info.keys())
    slicing_times = list(audio_info.values())
    slicing_times.append(audio.duration_seconds)
    no_output_files = len(audio_info)

    files_names = []
    urls = []
    
    for i in range(no_output_files):
        progress_percent = int(i / no_output_files * 100)
        current_task.update_state(
            state='PROGRESS',
            meta={
              'current': i,
              'total': no_output_files,
              'percent': progress_percent
            }
        )
        file_name = slugify(slicing_titles[i]) + ".mp3"
        files_names.append(file_name)
        
        song = get_song_audio(i, audio, slicing_times)
        file = song.export(format="mp3", bitrate="202")
        
        if upload:
            urls.append(upload_to_s3(file_name, file))
    
    if upload:
        return {'urls': urls, 'files_names': files_names}
    else:
        return {'files_names': files_names}


def extract_songs_info(text):
    """
    Extracts time information and title from each text line. There must be
    at least one valid line in the text, and zero invalid lines - only then
    function will return.
    :return: dict {string: int}
    """
    if not isinstance(text, str):
        raise AttributeError

    songs_info = {}
    
    for line in text.split('\n'):
        if line.isspace() or line == '':
            continue

        # Time info indicate songs' starting times.
        # Valid time form is " 'one or more digits':'two digits' "
        # f.e. 03:40, 3:40, 73:40, 125:00.
        match = re.search(TIME_FORMAT, line)
        if not match:
            raise ValueError

        time = match.group(0)
        hours, minute, second = time.split(':')
        time_in_seconds = 3600 * int(hours) + int(minute) * 60 + int(second)

        song = line.replace(time, '').replace('.', '').replace('\n', '')
        songs_info[song] = time_in_seconds

    if songs_info:
        return songs_info
    else:
        raise ValueError
