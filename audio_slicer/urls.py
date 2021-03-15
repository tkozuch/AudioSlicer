from django.urls import path
from slicing_app import views

urlpatterns = [
    path("", views.upload_file, name="main_view"),
    path("get_progress/", views.get_progress, name="get_progress"),
]
