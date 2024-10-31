from django.shortcuts import render
from hotel.models import Hotel, Booking,ActivityLog, StaffOnDuty, Room, RoomType
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import View
from django.utils import timezone
from django.core.exceptions import ValidationError



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
    
    print(hotel)  # For debugging: Check the fetched hotel object
    context = {
        "hotel": hotel  # Pass the hotel object to the template
    }
    return render(request, "hotel/hotel_detail.html", context)  # Render the detail template


from django.shortcuts import get_object_or_404

def room_type_detail(request, slug, rt_slug):
    hotel = get_object_or_404(Hotel, status="Live", slug=slug)
    room_type = get_object_or_404(RoomType, hotel=hotel, slug=rt_slug)
    rooms = Room.objects.filter(room_type=room_type, is_available=True)

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

        # Get other available rooms of the same room type
        available_rooms = Room.objects.filter(room_type=room_type, is_available=True).exclude(id=room.id)

        context = {
            "room": room,
            "available_rooms": available_rooms,
        }
        return render(request, "hotel/booking_form.html", context)

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        num_adults = int(request.POST.get('num_adults', 0))  # Default to 0 if not provided
        num_children = int(request.POST.get('num_children', 0))  # Default to 0 if not provided
        total_guests = num_adults + num_children

        # Check room capacity
        room_capacity = room.room_type.room_capacity
        if total_guests > room_capacity:
            return render(request, "hotel/booking_form.html", {
                "room": room,
                "error": f"Total guests ({total_guests}) exceed room capacity ({room_capacity})."
            })

        # Check room availability
        if not self.is_room_available(room, check_in_date, check_out_date):
            return render(request, "hotel/booking_form.html", {
                "room": room,
                "error": "Room is not available for the selected dates."
            })

        # Create the booking
        booking = Booking(
            user=request.user,
            hotel=room.hotel,
            room_type=room.room_type,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total=room.price(),  # Adjust total based on the number of guests if needed
            num_adults=num_adults,
            num_children=num_children,
            is_active=True,
            date=timezone.now()
        )
        booking.save()

        # Mark the room as unavailable
        room.is_available = False
        room.save()

        return redirect('hotel:booking_success', booking_id=booking.booking_id)

    def is_room_available(self, room, check_in_date, check_out_date):
        # Check if there are any bookings for this room in the given date range
        conflicting_bookings = Booking.objects.filter(
            room=room,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        )
        return not conflicting_bookings.exists()

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
        booking = get_object_or_404(Booking, booking_id=booking_id)
        context = {
            'booking': booking,  # Pass the entire booking object
        }
        return render(request, "hotel/booking_success.html", context)
