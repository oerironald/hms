from django.shortcuts import render
from hotel.models import Hotel, Booking,ActivityLog, StaffOnDuty, Room, RoomType
from django.shortcuts import get_object_or_404

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
    # Fetch the hotel based on the slug
    hotel = get_object_or_404(Hotel, status="Live", slug=slug)
    
    # Fetch the room type based on the hotel and room type slug
    room_type = get_object_or_404(RoomType, hotel=hotel, slug=rt_slug)
    
    # Get available rooms for this room type
    rooms = Room.objects.filter(room_type=room_type, is_available=True)
    
    # Prepare context for rendering the template
    context = {
        "hotel": hotel,
        "room_type": room_type,
        "rooms": rooms,
    }
    
    return render(request, "hotel/room_type_detail.html", context)


from django.shortcuts import redirect
from django.views import View
from django.utils import timezone

def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    context = {
        "rooms": rooms,
    }
    return render(request, "hotel/room_list.html", context)


class BookingView(View):
    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        context = {
            "room": room,
        }
        return render(request, "hotel/booking_form.html", context)

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        booking = Booking(
            user=request.user,
            hotel=room.hotel,
            room_type=room.room_type,
            check_in_date=request.POST.get('check_in_date'),
            check_out_date=request.POST.get('check_out_date'),
            total=room.price(),  # Simplified for example
            is_active=True,
            date=timezone.now()
        )
        booking.save()
        # Redirect to a success page or detail view
        return redirect('hotel:booking_success', booking_id=booking.booking_id)