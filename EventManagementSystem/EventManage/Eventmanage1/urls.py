from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage view
    path('events/', views.EventListView.as_view(), name='browse_events'),  # View all events
    path('events/create/', views.EventCreateView.as_view(), name='create_event'),  # Create new event
    path('events/update/<int:pk>/', views.EventUpdateView.as_view(), name='update_event'),  # Update existing event
    path('events/delete/<int:pk>/', views.EventDeleteView.as_view(), name='delete_event'),  # Delete event (POST only)

    path('book_ticket/<int:event_id>/', views.book_ticket, name='book_ticket'),  # Book a ticket
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),  # Booking confirmation

    path('register/', views.register, name='register'),  # User registration
    path('login/', views.login_view, name='login'),  # Login
    path('logout/', views.logout_view, name='logout'),  # Logout

    path('contact-sales/', views.contact_sales, name='contact_sales'),  # Contact sales

    path('admin-panel/', views.admin_panel, name='admin_panel'),  # Admin dashboard (if implemented)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
