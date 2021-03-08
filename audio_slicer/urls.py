from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from slicing_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.upload_file, name="main_view"),
    path("get_progress/", views.get_progress),
    # path('test/', views.test),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
