from django.contrib import admin
from hotel.models import Hotel, Booking, ActivityLog, StaffOnDuty, Room, RoomType

class HotelAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'user', 'status']
    prepopulated_fields = {"slug": ("name", )}

admin.site.register(Hotel, HotelAdmin)
