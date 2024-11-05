# hotel/views.py
from django.shortcuts import render
from hotel.models import Hotel, Booking,ActivityLog, StaffOnDuty, Room, RoomType
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import View
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError



def index(request):
    hotels = Hotel.objects.filter(status="Live")  # Fetch live hotels
    print(hotels)  # For debugging: Check what hotels are fetched
    context = {
        "hotels": hotels  # Pass the hotels context to the template
    }
    return render(request, "hotel/hotel_list.html", context)  # Ensure context is passed


# hotel/views.py




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


from django.shortcuts import get_object_or_404


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

        # Get all rooms of the same type
        all_rooms = Room.objects.filter(room_type=room_type)

        # Prepare to check availability for each room
        rooms_with_availability = []
        for room in all_rooms:
            is_available = self.is_room_available(room)  # Check overall availability for each room
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

        while True:
            check_in_date = request.POST.get(f'check_in_date_{index}')
            check_out_date = request.POST.get(f'check_out_date_{index}')
            if not check_in_date and not check_out_date:
                break  # Exit if no more forms

            num_adults = int(request.POST.get(f'num_adults_{index}', 0))
            num_children = int(request.POST.get(f'num_children_{index}', 0))

            # Skip if check-in or check-out date is missing
            if not check_in_date or not check_out_date:
                index += 1
                continue

            # Parse the datetime strings
            check_in = timezone.datetime.strptime(check_in_date, '%Y-%m-%dT%H:%M')
            check_out = timezone.datetime.strptime(check_out_date, '%Y-%m-%dT%H:%M')
            num_nights = (check_out - check_in).days

            total_guests = num_adults + num_children
            room_capacity = room.room_type.room_capacity

            # Check room capacity
            if total_guests > room_capacity:
                return render(request, "hotel/booking_form.html", {
                    "room": room,
                    "error": f"Total guests ({total_guests}) exceed room capacity ({room_capacity})."
                })

            # Check room availability for the selected dates
            if not self.is_room_available(room, check_in, check_out):
                return render(request, "hotel/booking_form.html", {
                    "room": room,
                    "error": "Room is already booked for the selected dates."
                })

            # Calculate total cost based on price per night and number of nights
            total_cost = room.price() * num_nights

            # Create the booking
            booking = Booking(
                user=request.user,
                hotel=room.hotel,
                room_type=room.room_type,
                check_in_date=check_in,
                check_out_date=check_out,
                total=total_cost,
                num_adults=num_adults,
                num_children=num_children,
                is_active=True,
                date=timezone.now()
            )
            booking.save()
            bookings_data.append(booking)

            # Mark the room as unavailable after booking
            room.is_available = False  # Update availability
            room.save()  # Save the room status

            index += 1  # Move to the next index

        # Redirect logic
        if bookings_data:
            return redirect('hotel:booking_success', booking_id=bookings_data[0].booking_id)  # Use booking_id
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