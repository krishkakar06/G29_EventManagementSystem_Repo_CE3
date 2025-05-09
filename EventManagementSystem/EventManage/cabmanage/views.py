from django.shortcuts import render, redirect, get_object_or_404
from .forms import CabBookingForm
from .models import CabBooking
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Eventmanage1.models import Event
from django.http import HttpResponseNotAllowed

@login_required
def book_cab(request):
    event_id = request.GET.get('event_id')
    event = None

    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            messages.warning(request, "Selected event not found.")

    if request.method == 'POST':
        form = CabBookingForm(request.POST)
        if form.is_valid():
            cab_booking = form.save(commit=False)
            cab_booking.user = request.user
            
            # Handle event linking
            if event:
                cab_booking.event = event
            else:
                # Capture event name from direct booking
                event_name = request.POST.get('event_name')
                if event_name:
                    cab_booking.event_name = event_name
                    
            cab_booking.save()
            messages.success(request, 'Cab booked successfully!')
            return redirect('cab_history')
    else:
        initial_data = {}
        if event:
            initial_data['drop_location'] = event.location
        form = CabBookingForm(initial=initial_data)

    previous_booking = CabBooking.objects.filter(user=request.user).order_by('-pickup_time').first()

    return render(request, 'book_cab.html', {
        'form': form,
        'event': event,
        'previous_booking': previous_booking,
    })

@login_required
def cab_history(request):
    if request.user.is_staff:
        bookings = CabBooking.objects.all().order_by('-pickup_time')

        # Get filter parameters
        username = request.GET.get('username')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Filter by username
        if username:
            bookings = bookings.filter(user__username__icontains=username)

        # Filter by date range
        if start_date and end_date:
            bookings = bookings.filter(
                pickup_time__date__range=[start_date, end_date]
            )

        context = {
            'bookings': bookings,
            'is_admin': True,
            'filter_username': username,
            'filter_start': start_date,
            'filter_end': end_date
        }
    else:
        bookings = CabBooking.objects.filter(user=request.user).order_by('-pickup_time')
        context = {'bookings': bookings, 'is_admin': False}

    return render(request, 'cab_history.html', context)

@login_required
def update_cab_booking(request, booking_id):
    booking = get_object_or_404(CabBooking, pk=booking_id)

    # Ensure only the user who created the booking or an admin can update it
    if not request.user.is_staff and booking.user != request.user:
        return HttpResponseNotAllowed(['POST', 'GET'])

    if request.method == 'POST':
        form = CabBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cab booking updated successfully!')
            return redirect('cab_history')
    else:
        form = CabBookingForm(instance=booking)

    return render(request, 'update_cab_booking.html', {'form': form, 'booking': booking})

@login_required
def cancel_cab_booking(request, booking_id):
    booking = get_object_or_404(CabBooking, pk=booking_id)

    # Ensure only the user who created the booking or an admin can cancel it
    if not request.user.is_staff and booking.user != request.user:
        return HttpResponseNotAllowed(['POST'])

    # Cancel the booking directly without rendering a template
    booking.delete()
    messages.success(request, 'Cab booking canceled successfully!')
    return redirect('cab_history')
