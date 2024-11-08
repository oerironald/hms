from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from userauths.models import User
from shortuuid.django_fields import ShortUUIDField
import shortuuid
from cloudinary.models import CloudinaryField

# Choices for hotel status
HOTEL_STATUS = (
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    ("Rejected", "Rejected"),
    ("In Review", "In Review"),
    ("Live", "Live"),
)

# Choices for icon types
ICON_TYPE = (
    ("Bootstrap Icons", "Bootstrap Icons"),
    ("Fontawesome Icons", "Fontawesome Icons"),
    ("Box Icons", "Box Icons"),
    ("Remi Icons", "Remi Icons"),
    ("Flat Icons", "Flat Icons"),
)

# Choices for payment status
PAYMENT_STATUS = (
    ('MPESA', 'M-Pesa'),
    ('CASH', 'Cash'),
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", "Initiated"),
    ("failed", "Failed"),
    ("refunding", "Refunding"),
    ("refunded", "Refunded"),
    ("unpaid", "Unpaid"),
    ("expired", "Expired"),
)

class Hotel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)  # Increased max_length for better name support
    description = models.TextField(null=True, blank=True)
    image = CloudinaryField('image')  # Change to ImageField
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=20, choices=HOTEL_STATUS, default="Live")
    tags = models.CharField(max_length=200, help_text="Separate tags with commas")
    views = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    hid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz")
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate slug if not already set
        if not self.slug or self.slug == "":
            self.slug = slugify(self.name) + "-" + shortuuid.uuid()[:4]
        super(Hotel, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe(f"<img src='{self.image.url}' width='50' height='50' style='object-fit: cover; border-radius: 6px;' />")


class HotelGallery(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    image = CloudinaryField('image')  # Change to ImageField
    hgid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz")

    def __str__(self):
        return str(self.hotel.name)

    class Meta:
        verbose_name_plural = "Hotel Gallery"


class HotelFeatures(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TYPE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Hotel Features"


class HotelFAQs(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.question)

    class Meta:
        verbose_name_plural = "Hotel FAQs"


class RoomType(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    number_of_beds = models.PositiveIntegerField(default=0)
    room_capacity = models.PositiveIntegerField(default=0)
    rtid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz")
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.hotel.name} - ({self.price})"

    def rooms_count(self):
        return Room.objects.filter(room_type=self).count()

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.type) + '-' + str(uniqueid).lower()
        super(RoomType, self).save(*args, **kwargs)


class Room(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=1000)
    is_available = models.BooleanField(default=True)
    rid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvwxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_type.type} - {self.hotel.name}"

    class Meta:
        verbose_name_plural = "Rooms"

    def price(self):
        return self.room_type.price

    def number_of_beds(self):
        return self.room_type.number_of_beds


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS)
    full_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=1000)
    phone = models.CharField(max_length=1000)
    hotel = models.ForeignKey('Hotel', on_delete=models.SET_NULL, null=True, blank=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ManyToManyField(Room)
    before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=False)
    checked_in_tracker = models.BooleanField(default=False)
    checked_out_tracker = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    mpesa_payment_intent = models.CharField(max_length=1000, null=True, blank=True)
    success_id = models.CharField(max_length=1000, null=True, blank=True)
    booking_id = ShortUUIDField(unique=True, length=10, max_length=20)

    # Add the following fields
    num_adults = models.IntegerField(default=1)  # Default to 1 adult
    num_children = models.IntegerField(default=0)  # Default to 0 children
    cash_payment_received = models.BooleanField(default=False)  # Track if cash payment was received

    def __str__(self):
        return f"{self.booking_id}"

    def rooms(self):
        return self.room.all().count()



class ActivityLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    guest_out = models.DateTimeField()
    guest_in = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.booking)


class StaffOnDuty(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=190, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_id}"


class RoomServices(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.code


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"