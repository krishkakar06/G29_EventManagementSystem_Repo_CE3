from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_cab, name='book_cab'),
    path('history/', views.cab_history, name='cab_history'),
    path('update/<int:booking_id>/', views.update_cab_booking, name='update_cab_booking'),
    path('cancel/<int:booking_id>/', views.cancel_cab_booking, name='cancel_cab_booking'),
]
