from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from hotel.models import Hotel, Booking, RoomType
from django.http import JsonResponse


@csrf_exempt
def check_room_availability(request):
    if request.method == "POST":
        id = request.POST.get("hotel-id")
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")
        adult = request.POST.get("adult")
        children = request.POST.get("children")
        room_type_slug = request.POST.get("room-type")

        hotel = Hotel.objects.get(id=id)
        room_type = RoomType.objects.get(hotel=hotel, slug=room_type_slug)

        # Redirect to the room type detail page with query parameters
        url = reverse("hotel:room_type_detail", args=[hotel.slug, room_type.slug])
        url_with_params = f"{url}?checkin={checkin}&checkout={checkout}&adult={adult}&children={children}"

        return HttpResponseRedirect(url_with_params)


def add_to_selection(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    room_selection = {}
    room_id = str(request.GET.get('id', ''))

    # Check if room_id is present
    if not room_id:
        return JsonResponse({'error': 'Room ID is required.'}, status=400)

    room_selection[room_id] = {
        'hotel_id': str(request.GET.get('hotel_id', '')),
        'hotel_name': str(request.GET.get('hotel_name', '')),
        'room_name': str(request.GET.get('room_name', '')),
        'room_price': str(request.GET.get('room_price', '')),
        'number_of_beds': str(request.GET.get('number_of_beds', '')),
        'room_number': str(request.GET.get('room_number', '')),
        'room_type': str(request.GET.get('room_type', '')),
        'room_id': str(request.GET.get('room_id', '')),
        'checkout': str(request.GET.get('checkout', '')),
        'checkin': str(request.GET.get('checkin', '')),
        'adult': int(request.GET.get('adult', '0') or 0),  # Ensure default is a string
        'children': int(request.GET.get('children', '0') or 0)  # Ensure default is a string
    }

    # Debugging output
    print("Room Selection Data:", room_selection)

    # Check if 'selection_data_obj' exists in the session
    if 'selection_data_obj' in request.session:
        selection_data = request.session['selection_data_obj']

        # Debugging output
        print("Current Selection Data (before update):", selection_data)

        # Update or add to selection data
        if room_id in selection_data:
            selection_data[room_id]['adult'] += room_selection[room_id]['adult']
            selection_data[room_id]['children'] += room_selection[room_id]['children']
        else:
            selection_data.update(room_selection)

        request.session['selection_data_obj'] = selection_data
    else:
        # Create new selection data in session
        request.session['selection_data_obj'] = room_selection

    # Prepare the response data
    response_data = {
        "data": request.session['selection_data_obj'],
        "total_selected_items": len(request.session['selection_data_obj'])
    }

    return JsonResponse(response_data)