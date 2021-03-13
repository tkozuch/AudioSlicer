import datetime
import json

from celery.result import AsyncResult
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.middleware import csrf
from django.shortcuts import render

from .forms import FileForm, SlicingInfoFormset
from .slicing import slice_audio_task


def upload_file(request):
    if request.method == "POST":
        audio_info_formset = SlicingInfoFormset(request.POST)
        file_form = FileForm(request.POST, request.FILES)

        if audio_info_formset.is_valid() and file_form.is_valid():
            text_info = _extract_formset_data(audio_info_formset)
            my_file = file_form.files["file"].file
            csrf_token = csrf.get_token(request)

            task = slice_audio_task.delay(my_file, text_info, upload=True)

            context = {"task_id": task.id, "my_csrf_token": csrf_token}

            return render(request, "slicing_app/slicing.html", context)
    else:
        audio_info_formset = SlicingInfoFormset(
            initial=[
                {"title": "1. You love me yeyeye", "time": datetime.time(0, 00, 00)},
                {"title": "2. Song 2", "time": datetime.time(0, 0, 10)},
                {"title": "3. Hey you", "time": datetime.time(0, 0, 20)},
            ]
        )

    return render(
        request,
        "slicing_app/upload.html",
        {"formset": audio_info_formset, "file_form": FileForm()},
    )


def get_progress(request):
    result = AsyncResult(request.POST["task_id"])
    response_data = {
        "state": result.state,
        "details": result.info,
    }
    if result.state == "SUCCESS":
        response_data = result.result

    print(f"Got progress on celery task: {response_data}")

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_download_urls(request):
    paths = request.POST.getlist("paths[]")
    fs = FileSystemStorage()

    urls = [fs.url(path) for path in paths]
    response_data = {"urls": urls}

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def _extract_formset_data(formset_):
    """
    Merge the data from multiple inputs into single string (a format which the application
    previously used.
    """
    result = {}

    for form in formset_.forms:
        title = form.cleaned_data.get("title")
        time = form.cleaned_data.get("time")
        if title and time:
            result[title] = time

    return result
