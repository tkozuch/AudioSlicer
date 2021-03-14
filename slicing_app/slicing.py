import datetime
import os
from io import BytesIO
from logging import getLogger
from typing import List

import boto3
from botocore.client import Config
from celery import current_task, shared_task
from django.template.defaultfilters import slugify
from pydub import AudioSegment

log = getLogger(__file__)


@shared_task()
def slice_audio_task(file: BytesIO, text_input: dict):
    """
    Delegate audio slicing to Celery worker.
    """
    # Thanks to this we have the ability to test underlying logic in isolation without
    # calling for complicated Celery testing logic.
    return slice_audio(file, text_input)


def slice_audio(file: BytesIO, text_input: dict):
    """
    Slice audio file according to information given in text input and upload it to AWS S3 Server.
    """
    audio = load_audio(file)

    slicing_titles = text_input.keys()
    slicing_times = text_input.values()
    files_names = [get_file_name(slicing_title) for slicing_title in slicing_titles]
    audio_fragments = get_audio_fragments(audio, slicing_times=list(slicing_times))

    no_output_files = len(text_input)
    download_urls = []

    for i in range(no_output_files):
        file = audio_fragments[i].export(format="mp3", bitrate="202")

        file_url = upload_to_s3(files_names[i], file, *_get_s3_credentials())
        download_urls.append(file_url)

        update_task_progress(part=i + 1, of_parts=no_output_files)

    return {"urls": download_urls, "files_names": files_names}


def get_audio_fragments(
    audio: AudioSegment, slicing_times: List[datetime.time]
) -> List[AudioSegment]:
    slicing_times_ms = list(map(_convert_to_miliseconds, slicing_times))
    slicing_times_ms.append(audio.duration_seconds * 1000)

    fragments = []
    for fragment_number in range(len(slicing_times)):
        beginning = slicing_times_ms[fragment_number]
        end = slicing_times_ms[fragment_number + 1]

        fragments.append(audio[beginning:end])

    return fragments


def get_file_name(slicing_title: str):
    return slugify(slicing_title) + ".mp3"


def load_audio(file: BytesIO):
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


def update_task_progress(part: int, of_parts: int):
    progress_percent = int(part / of_parts * 100)
    current_task.update_state(
        state="PROGRESS",
        meta={"current": part, "total": of_parts, "percent": progress_percent},
    )


def _convert_to_miliseconds(time: datetime.time):
    return (time.hour * 3600 + time.minute * 60 + time.second) * 1000


def _get_s3_credentials():
    try:
        access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        access_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        bucket_name = os.environ["S3_BUCKET"]
    except KeyError:
        raise EnvVarsMissingError(
            "3 of this environmental variables need to be set: "
            "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and S3_BUCKET"
        ) from KeyError

    return access_key_id, access_secret_key, bucket_name


class AudioLoadError(Exception):
    pass


class EnvVarsMissingError(KeyError):
    pass
