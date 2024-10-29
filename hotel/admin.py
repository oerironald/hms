from django.contrib import admin
from hotel.models import (
    Hotel, Booking, ActivityLog, StaffOnDuty,
    Room, RoomType, RoomServices, Notification,
    Coupon, Bookmark, HotelGallery, HotelFeatures, HotelFAQs
)


class HotelAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'user', 'status']
    prepopulated_fields = {"slug": ("name",)}


class BookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'hotel', 'check_in_date', 'check_out_date', 'total', 'payment_status']
    list_filter = ['hotel', 'payment_status', 'is_active']
    search_fields = ['full_name', 'email', 'phone']


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'guest_in', 'guest_out', 'description', 'date']
    list_filter = ['booking', 'date']


class StaffOnDutyAdmin(admin.ModelAdmin):
    list_display = ['booking', 'staff_id', 'date']


class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'is_available', 'room_type']
    list_filter = ['hotel', 'room_type', 'is_available']


class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'hotel', 'price', 'room_capacity']


class RoomServicesAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'name', 'price']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']
    search_fields = ['title']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'expiry_date']
    search_fields = ['code']


class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel']


class HotelGalleryAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'image']


class HotelFeaturesAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'name', 'icon']


class HotelFAQsAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'question', 'date']


# Register your models here
admin.site.register(Hotel, HotelAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(StaffOnDuty, StaffOnDutyAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(RoomServices, RoomServicesAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(HotelGallery, HotelGalleryAdmin)
admin.site.register(HotelFeatures, HotelFeaturesAdmin)
admin.site.register(HotelFAQs, HotelFAQsAdmin)