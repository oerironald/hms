
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'hotel'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<slug:slug>/', views.hotel_detail, name='hotel_detail'),
    path('detail/<slug:slug>/room-type/<slug:rt_slug>', views.room_type_detail, name='room_type_detail'),
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)