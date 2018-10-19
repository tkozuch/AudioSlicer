from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from upload import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_file),
    path('get_progress/', views.get_progress),
    path('get_download_urls/', views.get_download_urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
