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
    path('room-availability/', views.check_availability, name='check_availability'),
    path('mpesa_payment/<int:booking_id>/', views.mpesa_payment, name='mpesa_payment'),
    path('cash_payment/<int:booking_id>/', views.cash_payment, name='cash_payment'),
    path('mpesa_callback/', views.mpesa_callback, name='mpesa_callback'),
    path('generate_pdf/<int:booking_id>/', views.generate_pdf, name='generate_pdf'),  # Updated to booking_id
    path('booking_summary/<int:booking_id>/', views.booking_summary, name='booking_summary'),
    path('save_receipt/', views.save_receipt, name='save_receipt'),
    path('receipts/', views.list_receipts, name='list_receipts'),
    path('receipts/download/<str:filename>/', views.download_receipt, name='download_receipt'),

    # Other paths...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)