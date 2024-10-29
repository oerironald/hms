
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'hotel'

urlpatterns = [
    path('', views.index, name='index'),
    path('hotels/<slug:slug>/', views.hotel_detail, name='hotel_detail'),  # Hotel detail page
    path('hotels/<slug:slug>/room-types/<slug:rt_slug>/', views.room_type_detail, name='room_type_detail'),
    # Room type detail page
    path('rooms/', views.room_list, name='room_list'),  # List of rooms
    path('booking/<int:room_id>/', views.BookingView.as_view(), name='booking'),  # Booking page
    # Add more paths as needed
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)