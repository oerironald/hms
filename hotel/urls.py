# hotel/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'hotel'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<slug:slug>/', views.hotel_detail, name='hotel_detail'),  # Hotel detail page
    path('hotels/<slug:slug>/room-types/<slug:rt_slug>/', views.room_type_detail, name='room_type_detail'),  # Room type detail page
    path('rooms/', views.room_list, name='room_list'),  # List of rooms
    path('booking/<int:room_id>/', views.BookingView.as_view(), name='booking'),  # Booking page
    path('booking/cancel/<str:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),  # Cancel booking
    path('booking/success/<str:booking_id>/', views.BookingSuccessView.as_view(), name='booking_success'),
    path('booking/failure/', views.BookingFailureView.as_view(), name='booking_failure'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)