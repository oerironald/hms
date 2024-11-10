# hotel/views.py
from hotel.models import Hotel, Booking,ActivityLog, StaffOnDuty, Room, RoomType
from django.views import View
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Room, Booking  # Adjust as per your models
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from dateutil import parser
from django_daraja.mpesa.core import MpesaClient
from .models import Booking
from django.shortcuts import get_object_or_404
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from xhtml2pdf import pisa
from datetime import datetime

def index(request):
    hotels = Hotel.objects.filter(status="Live")  # Fetch live hotels
    print(hotels)  # For debugging: Check what hotels are fetched
    context = {
        "hotels": hotels  # Pass the hotels context to the template
    }
    return render(request, "hotel/hotel_list.html", context)  # Ensure context is passed



def hotel_detail(request, slug):
    # Use get_object_or_404 to fetch a single hotel or return a 404 if not found
    hotel = get_object_or_404(Hotel, status="Live", slug=slug)

    # Fetch the rooms associated with the hotel
    rooms = Room.objects.filter(hotel=hotel)  # Adjust the field based on your model

    context = {
        "hotel": hotel,  # Pass the hotel object to the template
        "rooms": rooms,  # Pass the rooms list to the template
    }
    return render(request, "hotel/hotel_detail.html", context)  # Render the detail template



def room_type_detail(request, slug, rt_slug):
    hotel = get_object_or_404(Hotel, status="Live", slug=slug)
    room_type = get_object_or_404(RoomType, hotel=hotel, slug=rt_slug)
    # Get all rooms for the specified room type
    rooms = Room.objects.filter(room_type=room_type)

    # Get query parameters for availability
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    adult = request.GET.get('adult')
    children = request.GET.get('children')

    context = {
        "hotel": hotel,
        "room_type": room_type,
        "rooms": rooms,
        "checkin": checkin,
        "checkout": checkout,
        "adult": adult,
        "children": children,
    }

    return render(request, "hotel/room_type_detail.html", context)



def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    context = {
        "rooms": rooms,
    }
    return render(request, "hotel/room_list.html", context)


class BookingView(View):
    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        room_type = room.room_type

        all_rooms = Room.objects.filter(room_type=room_type)
        rooms_with_availability = []
        for room in all_rooms:
            is_available = self.is_room_available(room)
            rooms_with_availability.append({
                'room': room,
                'is_available': is_available
            })

        context = {
            "room": room,
            "rooms_with_availability": rooms_with_availability,
        }
        return render(request, "hotel/booking_form.html", context)

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        bookings_data = []
        index = 0

        # Capture the payment method from the form
        payment_method = request.POST.get('payment_method')  # 'MPESA' or 'CASH'

        while True:
            check_in_date = request.POST.get(f'check_in_date_{index}')
            check_out_date = request.POST.get(f'check_out_date_{index}')
            if not check_in_date and not check_out_date:
                break

            num_adults = int(request.POST.get(f'num_adults_{index}', 0))
            num_children = int(request.POST.get(f'num_children_{index}', 0))

            if not check_in_date or not check_out_date:
                index += 1
                continue

            check_in = timezone.datetime.strptime(check_in_date, '%Y-%m-%dT%H:%M')
            check_out = timezone.datetime.strptime(check_out_date, '%Y-%m-%dT%H:%M')
            num_nights = (check_out - check_in).days

            total_guests = num_adults + num_children
            room_capacity = room.room_type.room_capacity

            if total_guests > room_capacity:
                return render(request, "hotel/booking_form.html", {
                    "room": room,
                    "error": f"Total guests ({total_guests}) exceed room capacity ({room_capacity})."
                })

            if not self.is_room_available(room, check_in, check_out):
                return render(request, "hotel/booking_form.html", {
                    "room": room,
                    "error": "Room is already booked for the selected dates."
                })

            total_cost = room.price() * num_nights

            # Create booking and add payment method
            booking = Booking(
                user=request.user if request.user.is_authenticated else None,
                hotel=room.hotel,
                room_type=room.room_type,
                check_in_date=check_in,
                check_out_date=check_out,
                total=total_cost,
                num_adults=num_adults,
                num_children=num_children,
                is_active=True,
                date=timezone.now(),
                payment_status=payment_method,  # Save payment method
            )

            if payment_method == 'CASH':
                booking.cash_payment_received = False  # Initially set to False, will be updated later

            booking.save()
            bookings_data.append(booking)

            room.is_available = False
            room.save()

            index += 1

        if bookings_data:
            return redirect('hotel:booking_success', booking_id=bookings_data[0].booking_id)
        else:
            return redirect('hotel:booking_failure')

    def is_room_available(self, room, check_in_date=None, check_out_date=None):
        if check_in_date and check_out_date:
            conflicting_bookings = Booking.objects.filter(
                room=room,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date,
                is_active=True
            )
            return not conflicting_bookings.exists()
        else:
            return room.is_available

class CancelBookingView(View):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, booking_id=booking_id)

        # Update room availability
        rooms = booking.room.all()
        for room in rooms:
            room.is_available = True
            room.save()

        booking.delete()  # Or set is_active to False

        return redirect('hotel:booking_list')  # Redirect to a page with bookings


class BookingSuccessView(View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, booking_id=booking_id)  # Change to booking_id
        return render(request, 'hotel/booking_success.html', {'booking': booking})

class BookingFailureView(View):
    def get(self, request):
        return render(request, 'hotel/booking_failure.html')

def check_availability(request):
    available_rooms = None
    if request.method == "POST":
        check_in_date_str = request.POST.get('check_in_date')
        check_out_date_str = request.POST.get('check_out_date')
        num_guests = int(request.POST.get('num_guests'))

        # Convert to datetime using strptime
        check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%dT%H:%M')
        check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%dT%H:%M')

        # Step 1: Query to find available rooms based on room type capacity
        available_rooms = Room.objects.filter(
            is_available=True,
            room_type__room_capacity__gte=num_guests,  # Use the related field
        ).distinct()  # Use distinct to avoid duplicates if a room is available

        # Step 2: Check for existing bookings that overlap with the requested dates
        existing_bookings = Booking.objects.filter(
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            room__hotel__in=[room.hotel for room in available_rooms]  # Limit to the hotels of available rooms
        )

        # Exclude rooms that are booked
        booked_room_ids = existing_bookings.values_list('room', flat=True)
        available_rooms = available_rooms.exclude(id__in=booked_room_ids)

    return render(request, 'hotel/check_availability.html', {'available_rooms': available_rooms})


from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json

import logging

@csrf_exempt
def mpesa_payment(request, booking_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        phone_number = data.get("phone_number")
        paid_amount = data.get("paid_amount")

        if not phone_number or not paid_amount:
            return HttpResponseBadRequest("Phone number and paid amount are required")

        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]

        try:
            room = Room.objects.get(id=booking_id)
            booking = Booking.objects.filter(room=room, is_active=True).first()

            if not booking:
                return JsonResponse({"error": "No active booking found for this room"}, status=404)

            # Initialize the MpesaClient
            mpesa_client = MpesaClient()  # Create an instance of the MpesaClient

            # Assuming you have a valid callback_url defined somewhere
            callback_url = "https://your-domain.com/hotel/mpesa_callback/"

            response = mpesa_client.stk_push(phone_number, int(paid_amount), "Booking", "Room booking payment", callback_url)

            if response.status_code == 200:
                response_data = response.json()

                if response_data.get("ResponseCode") == "0":
                    # Mark room as unavailable
                    room.is_available = False
                    room.save()

                    # Use the existing booking's check-in date to format the filename
                    check_in_datetime = booking.check_in_date.strftime('%Y%m%d_%H%M%S')  # Include hours and minutes
                    pdf_filename = f"{phone_number}_{check_in_datetime}.pdf"

                    # Create PDF receipt (implement this function)
                    create_pdf_receipt(booking, pdf_filename)

                    return JsonResponse({"ResponseCode": "0", "message": "Payment initiated successfully", "receipt": pdf_filename}, status=200)

                else:
                    return JsonResponse({"ResponseCode": response_data.get("ResponseCode", "Unknown"), "message": response_data.get("errorMessage", "Payment failed")}, status=400)

            else:
                return JsonResponse({"error": "M-Pesa API request failed"}, status=400)

        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def cash_payment(request, booking_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            check_in_date = data.get("check_in_date")
            check_out_date = data.get("check_out_date")
            paid_amount = float(data.get("paid_amount"))

            if not check_in_date or not check_out_date or paid_amount is None:
                return HttpResponseBadRequest("Check-in date, check-out date, and paid amount are required")

            check_in_date = timezone.make_aware(parser.parse(check_in_date))
            check_out_date = timezone.make_aware(parser.parse(check_out_date))

            room = Room.objects.get(id=booking_id)

            if not room.is_available:
                return JsonResponse({"error": "Room is not available for the selected dates"}, status=400)

            room_type = room.room_type
            total_amount = room_type.price * (check_out_date - check_in_date).days

            if paid_amount < total_amount:
                return JsonResponse({"error": "Paid amount is less than the total amount"}, status=400)

            booking = Booking.objects.create(
                user=None,
                payment_status="CASH",
                room_type=room_type,
                hotel=room_type.hotel,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                num_adults=int(data.get("num_adults", 1)),
                num_children=int(data.get("num_children", 0)),
                total=total_amount,
                before_discount=total_amount,
                cash_payment_received=True,
                is_active=True
            )

            booking.room.add(room)
            room.is_available = False
            room.save()

            # Generate receipt PDF filename
            check_in_datetime = check_in_date.strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"{data.get('phone_number')}_{check_in_datetime}.pdf"

            # Create PDF receipt
            create_pdf_receipt(booking, pdf_filename)

            return JsonResponse({
                "success": True,
                "message": "Cash payment recorded successfully",
                "receipt": pdf_filename
            }, status=200)

        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def create_pdf_receipt(booking, filename):
    # Implement your PDF generation logic here
    # Use the filename to save the PDF
    pass

def mpesa_callback(request):
    # Handle the callback from M-Pesa
    if request.method == 'POST':
        # Log or process the incoming data
        data = request.body.decode('utf-8')  # Get the response data from M-Pesa
        print(f"Callback data: {data}")  # Optionally log the response

        # You may want to save payment status, transaction details, etc.
        # Process the callback here, then respond with success
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)



def generate_pdf(request, booking_id):
    # Fetch the booking object
    booking = get_object_or_404(Booking, id=booking_id)

    # Render the HTML template for the PDF
    html_string = render_to_string('hotel/receipt_template.html', {'booking': booking})

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{booking_id}.pdf"'

    # Create PDF from HTML
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF.', status=500)

    return response


def booking_summary(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    context = {
        'booking': booking,
    }
    return render(request, 'hotel/booking_summary.html', context)




@csrf_exempt  # Ensure proper CSRF handling in production
def save_receipt(request):
    if request.method == 'POST':
        try:
            # Load JSON data
            data = json.loads(request.body)
            receipt_content = data.get('receipt_content')
            phone_number = data.get('phone_number')  # Get phone number
            check_in_date_str = data.get('check_in_date')  # Get check-in date from request

            if receipt_content and phone_number and check_in_date_str:
                # Parse the check-in date
                check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%dT%H:%M')  # Adjust format if necessary
                formatted_date = check_in_date.strftime('%Y%m%d')  # Format date as YYYYMMDD

                # Define the path to save the receipt using phone number and check-in date
                filename = f'{phone_number}_{formatted_date}.pdf'  # Use phone number and formatted check-in date
                save_path = os.path.join(settings.BASE_DIR, 'hotel', 'receipts', filename)

                # Convert HTML to PDF
                with open(save_path, 'wb') as pdf_file:
                    pisa_status = pisa.CreatePDF(receipt_content, dest=pdf_file)

                if pisa_status.err:
                    return JsonResponse({'success': False, 'error': 'Failed to create PDF.'}, status=400)

                return JsonResponse({'success': True, 'filename': filename}, status=200)

            return JsonResponse({'success': False, 'error': 'No receipt content, phone number, or check-in date provided.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False}, status=400)