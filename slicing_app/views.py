import json

from django.http import HttpResponse
from django.shortcuts import render
from django.middleware import csrf
from django.core.files.storage import FileSystemStorage
from celery.result import AsyncResult

from .forms import UploadFileForm
from .slicing import slice_audio


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            text_info = request.POST.get('title')
            my_file = request.FILES['file'].file
            csrf_token = csrf.get_token(request)
            
            task = slice_audio.delay(my_file, text_info)
            
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
        response_data = result.result
        
    return HttpResponse(json.dumps(response_data), content_type='application/json')


def get_download_urls(request):
    paths = request.POST.getlist('paths[]')
    fs = FileSystemStorage()
    urls = [fs.url(path) for path in paths]
    response_data = {'urls': urls}
    
    return HttpResponse(json.dumps(response_data), content_type='application/json')
