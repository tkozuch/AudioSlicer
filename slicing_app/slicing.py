import datetime
import os
from io import BytesIO
from logging import getLogger

import boto3
from botocore.client import Config
from celery import current_task, shared_task
from django.template.defaultfilters import slugify
from pydub import AudioSegment

log = getLogger(__file__)


@shared_task()
def slice_audio(file: BytesIO, text_input: dict, upload: bool = False):
    """
    Slices audio file according to information given in text input.
    """
    audio = load_audio(file)

    slicing_titles = list(text_input.keys())
    slicing_times = list(map(_convert_to_miliseconds, text_input.values()))
    slicing_times.append(audio.duration_seconds * 1000)

    no_output_files = len(text_input)
    files_names = []
    download_urls = []

    for file_part_number in range(no_output_files):
        file_name = slugify(slicing_titles[file_part_number]) + ".mp3"
        files_names.append(file_name)

        beginning = slicing_times[file_part_number]
        end = slicing_times[file_part_number + 1]
        audio_fragment = audio[beginning:end]

        file = audio_fragment.export(format="mp3", bitrate="202")

        if upload:
            file_url = upload_to_s3(file_name, file, *_get_s3_credentials())
            download_urls.append(file_url)

        update_task_progress(file_part_number, no_output_files)

    return (
        {"urls": download_urls, "files_names": files_names}
        if upload
        else {"files_names": files_names}
    )


def load_audio(file):
    try:
        audio = AudioSegment.from_mp3(file)
    except Exception as exc:  # TODO: Add custom exception.
        log.exception(f"Problem loading audio: \n{exc}")
        raise AudioLoadError(exc)
    else:
        log.info("Successfully loaded audio")
    return audio


def upload_to_s3(key, file, access_key_id, access_secret_key, bucket_name):
    """
    Upload to Amazon S3 service.
    :return: url for the uploaded file
    """
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_secret_key,
        config=Config(signature_version="s3v4"),
    )
    log.info(f"Uploading to S3: {key} | {file}")
    s3.Bucket(bucket_name).put_object(Key=key, Body=file, ACL="public-read")
    url = "https://s3.eu-central-1.amazonaws.com/{}/{}".format(bucket_name, key)

    return url


def update_task_progress(file_part_number, no_output_files):
    progress_percent = int(file_part_number / no_output_files * 100)
    current_task.update_state(
        state="PROGRESS",
        meta={"current": file_part_number, "total": no_output_files, "percent": progress_percent},
    )


def _convert_to_miliseconds(time: datetime.time):
    return (time.hour * 3600 + time.minute * 60 + time.second) * 1000


def _get_s3_credentials():
    access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
    access_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    bucket_name = os.environ["S3_BUCKET"]

    return access_key_id, access_secret_key, bucket_name


class AudioLoadError(Exception):
    pass
