from django.core.management.base import BaseCommand
from django.utils import timezone
from hotel.models import Room, Booking

class Command(BaseCommand):
    help = 'Mark rooms as available after checkout'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Get all bookings where checkout time has passed
        expired_bookings = Booking.objects.filter(check_out_date__lt=now, is_active=True)

        for booking in expired_bookings:
            # Assuming booking.room is a related name for a many-to-many relation
            for room in booking.room.all():  # Iterate over each room in the booking
                room.is_available = True  # Mark the room as available
                room.save()  # Save the room status
            # Optionally, mark the booking as inactive or completed
            booking.is_active = False
            booking.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated room availability.'))