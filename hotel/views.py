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