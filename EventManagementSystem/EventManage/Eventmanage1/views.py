from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Event, Booking, Contact
from .forms import EventForm, BookingForm, ContactForm, RegisterForm, LoginForm
from .decorators import role_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseNotAllowed,HttpResponseForbidden,HttpResponseRedirect
from itertools import groupby
from operator import itemgetter
from django.core.mail import send_mail
from django.conf import settings
from cabmanage.models import CabBooking
from django.views.decorators.http import require_http_methods
import requests
import datetime
from decimal import Decimal
token = 'abcdefghi'  
from django.conf import settings

# Remove usage of FLASK_API_CONFIG which is not defined in settings
# Use FLASK_API_URL and FLASK_API_TOKEN directly from settings

# Utility Functions
def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

# Home and Public Views
def home(request):
    return render(request, 'home.html')
API_URL = settings.FLASK_API_URL

import json

TOKEN = 'abcdefghi'  # Must match Flask API token
HEADERS = {'Authorization': f'Bearer {TOKEN}'}
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
import requests
from django.conf import settings
from .models import Event
from .forms import EventForm

class EventListView(ListView):
    model = Event
    template_name = 'browse_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Get search query from query params
        search_query = self.request.GET.get('search', '').lower()
        filter_category = self.request.GET.get('category', '').lower()

        response = requests.get(f"{settings.FLASK_API_URL}/events")
        if response.status_code != 200:
            return []

        events = response.json()

        # Map 'image' field to 'image_url' for template compatibility
        import logging
        logger = logging.getLogger(__name__)
        for event in events:
            image_path = event.get('image', None)
            if image_path and not image_path.startswith('http'):
                base_url = getattr(settings, 'FLASK_MEDIA_URL', '').rstrip('/')
                if image_path.startswith(base_url):
                    event['image_url'] = image_path
                elif image_path.startswith('/uploads'):
                    # Remove leading /uploads to avoid duplication
                    image_path_clean = image_path[len('/uploads'):]
                    event['image_url'] = f"{base_url}{image_path_clean}"
                else:
                    image_path_clean = image_path.lstrip('/')
                    event['image_url'] = f"{base_url}/{image_path_clean}"
                logger.debug(f"Constructed image_url: {event['image_url']}")
            else:
                event['image_url'] = image_path

        # Filter by search query if provided
        if search_query:
            events = [e for e in events if search_query in e.get('title', '').lower() or search_query in e.get('description', '').lower()]

        # Filter by category if provided
        if filter_category:
            events = [e for e in events if e.get('type', '').lower() == filter_category]

        # Sort events by date ascending
        try:
            events.sort(key=lambda e: e.get('date', ''))
        except Exception:
            pass

        # Group events by type for template
        from collections import defaultdict
        grouped_events = defaultdict(list)
        for event in events:
            grouped_events[event.get('type', 'Other')].append(event)

        # Convert to list of dicts for template compatibility
        grouped_list = [{'category': k, 'events': v} for k, v in grouped_events.items()]

        # Extract categories list for filter buttons
        categories = sorted(set(event.get('type', 'Other') for event in events))

        self.extra_context = {'categories': categories}

        return grouped_list

from django.utils.decorators import method_decorator
from .decorators import role_required

@method_decorator(role_required(allowed_roles=['admin']), name='dispatch')
class EventCreateView(CreateView):
    form_class = EventForm
    template_name = 'create_event.html'
    success_url = reverse_lazy('browse_events')

    def form_valid(self, form):
        data = form.cleaned_data.copy()  # Make a mutable copy
        data['organizer_id'] = self.request.user.profile.flask_user_id

        # Convert date to string for JSON serialization
        if isinstance(data.get('date'), (datetime.date, datetime.datetime)):
            data['date'] = data['date'].isoformat()

        # Convert Decimal to float for JSON serialization
        if isinstance(data.get('price'), Decimal):
            data['price'] = float(data['price'])

        # Handle image path from hidden input (async upload)
        image_path = self.request.POST.get('image_url', '')
        if image_path:
            data['image'] = image_path
        
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Sending event creation data to Flask API: {data}")
        try:
            response = requests.post(
                f"{settings.FLASK_API_URL}/events",
                json=data,
                headers={'Authorization': f'Bearer {settings.FLASK_API_TOKEN}'}
            )
            if response.status_code == 201:
                messages.success(self.request, "Event created successfully!")
                return super().form_valid(form)
            else:
                messages.error(self.request, f"Failed to create event: {response.text}")
                return self.form_invalid(form)
        except requests.RequestException as e:
            messages.error(self.request, f"Event creation error: {e}")
            return self.form_invalid(form)

@method_decorator(role_required(allowed_roles=['admin']), name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    template_name = 'update_event.html'
    success_url = reverse_lazy('browse_events')

    def get_form_class(self):
        from .forms import EventForm
        # Exclude image field to avoid validation error on string path
        class EventUpdateForm(EventForm):
            class Meta(EventForm.Meta):
                exclude = ['image']
        return EventUpdateForm

    def get_object(self):
        # Return None or a dummy object because we override get_initial
        return None

    def get_initial(self):
        response = requests.get(f"{settings.FLASK_API_URL}/events/{self.kwargs['pk']}")
        if response.status_code == 200:
            return response.json()
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = requests.get(f"{settings.FLASK_API_URL}/events/{self.kwargs['pk']}")
        if response.status_code == 200:
            context['event'] = response.json()
        else:
            context['event'] = {}
        return context

    def form_valid(self, form):
        data = form.cleaned_data.copy()

        # Convert date to string for JSON serialization
        if isinstance(data.get('date'), (datetime.date, datetime.datetime)):
            data['date'] = data['date'].isoformat()

        # Convert Decimal to float for JSON serialization
        if isinstance(data.get('price'), Decimal):
            data['price'] = float(data['price'])

        # Handle image path from hidden input (async upload)
        image_path = self.request.POST.get('image_url', '')
        if image_path:
            data['image'] = image_path

        try:
            response = requests.put(
                f"{settings.FLASK_API_URL}/events/{self.kwargs['pk']}",
                json=data,
                headers={'Authorization': f'Bearer {settings.FLASK_API_TOKEN}'}
            )
            if response.status_code == 200:
                messages.success(self.request, "Event updated successfully!")
                return super().form_valid(form)
            else:
                messages.error(self.request, f"Failed to update event: {response.text}")
                return self.form_invalid(form)
        except requests.RequestException as e:
            messages.error(self.request, f"Event update error: {e}")
            return self.form_invalid(form)

@method_decorator(role_required(allowed_roles=['admin']), name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('browse_events')

    def get_object(self):
        response = requests.get(f"{settings.FLASK_API_URL}/events/{self.kwargs['pk']}")
        return response.json()

    def get(self, request, *args, **kwargs):
        # Override GET to delete immediately without confirmation template
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            response = requests.delete(
                f"{settings.FLASK_API_URL}/events/{self.kwargs['pk']}",
                headers={'Authorization': f'Bearer {settings.FLASK_API_TOKEN}'}
            )
            if response.status_code == 200:
                messages.success(request, "Event deleted successfully!")
            else:
                messages.error(request, f"Failed to delete event: {response.text}")
        except requests.RequestException as e:
            messages.error(request, f"Event deletion error: {e}")
        return redirect(self.success_url)

# Booking Views
import logging

logger = logging.getLogger(__name__)

@login_required
@role_required(allowed_roles=['user'])
def book_ticket(request, event_id):
    # Fetch event data from Flask API instead of Django ORM
    try:
        response = requests.get(f"{settings.FLASK_API_URL}/events/{event_id}")
        if response.status_code == 200:
            event = response.json()
            # Map image to image_url with full URL
            image_path = event.get('image', None)
            if image_path and not image_path.startswith('http'):
                base_url = settings.FLASK_API_URL.rstrip('/')
                if base_url.endswith('/api'):
                    base_url = base_url[:-4]  # remove '/api'
                event['image_url'] = f"{base_url}{image_path}"
            else:
                event['image_url'] = image_path
        else:
            messages.error(request, "Event not found.")
            return redirect('browse_events')
    except requests.RequestException as e:
        messages.error(request, f"Error fetching event: {e}")
        logger.error(f"Error fetching event {event_id}: {e}")
        return redirect('browse_events')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            # Since event is a dict from API, we need to get or create Django Event instance
            event_obj, created = Event.objects.get_or_create(
                flask_id=event['id'],
                defaults={
                    'title': event['title'],
                    'description': event['description'],
                    'type': event['type'],
                    'price': event['price'],
                    'date': event['date'],
                    'location': event['location'],
                    'image': event.get('image', ''),
                    'organizer': request.user  # or None if unknown
                }
            )
            booking.event = event_obj
            booking.user = request.user
            booking.save()
            messages.success(request, f'Booking successful! Your booking ID is {booking.id}')
            return redirect('booking_confirmation', booking_id=booking.id)
        else:
            messages.error(request, "Invalid booking form submission.")
            logger.warning(f"Invalid booking form submission for event {event_id} by user {request.user.id}")
    else:
        form = BookingForm()
    return render(request, 'book_ticket.html', {'form': form, 'event': event})

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    total_price = booking.tickets * booking.event.price 

    return render(request, 'booking_confirmation.html', {
        'booking': booking,
        'total_price': total_price,
        'event_id': booking.event.id, 
    })

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            role = form.cleaned_data.get('role', 'user') 
            if role == 'admin':  
                user.is_staff = True  
            user.save() 

            # Create user in Flask API and get flask_user_id
            flask_user_id = None
            try:
                flask_response = requests.post(
                    f"{settings.FLASK_API_URL}/users",
                    json={
                        "username": user.username,
                        "email": user.email,
                        "role": role
                    },
                    headers={'Authorization': f'Bearer {settings.FLASK_API_TOKEN}'}
                )
                if flask_response.status_code == 201:
                    flask_user_id = flask_response.json().get('id')
            except Exception as e:
                print(f"Error creating user in Flask API: {e}")

            Profile.objects.create(
                user=user,
                role=role,
                flask_user_id=flask_user_id
            )
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next', '') 

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                next_url = request.POST.get('next', '') 
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                
                if is_admin(user):
                    return redirect('admin_panel')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password') 
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'next': next_url if next_url.startswith('/') else ''  # Pass next_url to the template
    })

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('home')

# Contact View

from django.db.models import Sum, F, ExpressionWrapper, FloatField

def admin_panel(request):
    # Fetch events count
    events_count = Event.objects.count()

    # Fetch bookings count
    bookings_count = Booking.objects.count()

    # Calculate total revenue (sum of tickets * event price)
    total_revenue = Booking.objects.annotate(
        total_price=ExpressionWrapper(F('tickets') * F('event__price'), output_field=FloatField())
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Fetch recent bookings (latest 10)
    recent_bookings = Booking.objects.annotate(
        total_price=ExpressionWrapper(F('tickets') * F('event__price'), output_field=FloatField())
    ).order_by('-id')[:10]

    context = {
        'events_count': events_count,
        'bookings_count': bookings_count,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin_panel.html', context)


@login_required
def contact_sales(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, 'Thank you for contacting us! Our sales team will get back to you soon.')
            return redirect('contact_sales')
    else:
        form = ContactForm()
    
    return render(request, 'contact_sales.html', {'form': form})
