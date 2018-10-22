import os
import json
import boto3
from django.http import HttpResponse
from django.shortcuts import render
from django.middleware import csrf
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from celery.result import AsyncResult

from .forms import UploadFileForm
from .slicing import slice_audio


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            text_info = request.POST.get('title')
            my_file = request.FILES['file']

            file_name = FileSystemStorage().save(my_file.name, my_file)
            local_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            task = slice_audio.delay(local_file_path, text_info)
            csrf_token = csrf.get_token(request)
            context = {'task_id': task.id, 'my_csrf_token': csrf_token }
            return render(request, 'slicing_app/slicing.html', context)
        else:
            return HttpResponse(json.dumps({'task_id': None}),
                                content_type='application/json')
    else:
        form = UploadFileForm
    return render(request, 'slicing_app/upload.html', {'form': form})


def get_progress(request):
    result = AsyncResult(request.POST['task_id'])
    response_data = {
        'state': result.state,
        'details': result.info,
    }
    if result.state == 'SUCCESS':
        response_data['return_value'] = result.result
    return HttpResponse(json.dumps(response_data), content_type='application/json')


def get_download_urls(request):
    paths = request.POST.getlist('paths[]')
    fs = FileSystemStorage()
    urls = [fs.url(path) for path in paths]
    response_data = {'urls': urls}
    return HttpResponse(json.dumps(response_data), content_type='application/json')


def sign_s3(request):
    print("jestem w sign_s3")
    S3_BUCKET = os.environ.get('S3_BUCKET')
    
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')
    
    s3 = boto3.client('s3')
    
    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = {"acl": "public-read", "Content-Type": file_type},
        Conditions = [
          {"acl": "public-read"},
          {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )
    data = json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })
    
    return HttpResponse(data, content_type='json')