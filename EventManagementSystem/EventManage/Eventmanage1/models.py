from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    flask_id = models.IntegerField(null=True, blank=True)
  # Reference to Flask
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    image = models.URLField(blank=True, default='')
    organizer =models.ForeignKey(User, on_delete=models.CASCADE, null=True) # Reference to Flask
    EVENT_TYPE_CHOICES = [
        ('Music', 'Music'),
        ('Food', 'Food'),
        ('Business', 'Business'),
        ('Dance', 'Dance'),
        ('Education', 'Education'),
        ('Wedding', 'Wedding'),
    ]

    
    type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='other'
    )
    class Meta:
        pass


    def __str__(self):
        return self.title

class Booking(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='bookings')
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    tickets = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user_name} - {self.event.title}"


class Ticket(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    quantity = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} x{self.quantity}"


class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    company_name = models.CharField(max_length=100)
    organization_type = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    tickets_planned = models.IntegerField()
    average_cost = models.FloatField()
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company_name}"
    

class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    flask_user_id = models.IntegerField(null=True)
    def __str__(self):
        return f"{self.user.username} - {self.role}"
