from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Contact, Event, Booking, Profile
from django.core.validators import validate_email
from django.utils import timezone
from django.contrib.auth import authenticate

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%d']
    )
    
    price = forms.DecimalField(
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'type', 'image', 'price', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'minlength': 50
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError("Price is required")
        if price < 0:
            raise ValidationError("Price cannot be negative")
        return price

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past")
        return date

class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes and attributes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name != 'organization_type' and field_name != 'country':
                field.widget.attrs['placeholder'] = self.get_placeholder(field_name)
            if field_name in ['tickets_planned', 'average_cost']:
                field.widget.attrs['min'] = '1'
            if field_name == 'average_cost':
                field.widget.attrs['step'] = '0.01'
            
            # Add required attribute for client-side validation
            if field.required:
                field.widget.attrs['required'] = 'required'

    def get_placeholder(self, field_name):
        placeholders = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company_name': 'Acme Inc',
            'phone_number': 'Enter your phone number',  # No format requirements
            'tickets_planned': '100',
            'average_cost': '50.00',
            'reason': 'Tell us about your event needs'  # No length requirement
        }
        return placeholders.get(field_name, '')

    phone_number = forms.CharField(
        max_length=20,
        help_text="Enter your phone number in any format"
    )

    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Describe your event needs"
    )

    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'company_name',
            'organization_type', 'phone_number', 'country',
            'tickets_planned', 'average_cost', 'reason'
        ]
        widgets = {
            'organization_type': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Organization type'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Country'
            }),
        }
        error_messages = {
            'email': {
                'invalid': "Please enter a valid email address (e.g. name@example.com)"
            },
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Please enter a valid email address")
        return email

    def clean_tickets_planned(self):
        tickets = self.cleaned_data['tickets_planned']
        if tickets < 1:
            raise ValidationError("Number of tickets must be at least 1")
        if tickets > 1000000:
            raise ValidationError("For large orders (>1M tickets), please call our sales team")
        return tickets

    def clean_average_cost(self):
        cost = self.cleaned_data['average_cost']
        if cost <= 0:
            raise ValidationError("Average cost must be greater than 0")
        if cost > 10000:
            raise ValidationError("For premium tickets (>$10,000), please call our sales team")
        return round(cost, 2)
    
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user_name', 'user_email', 'tickets']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'user_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'tickets': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Create password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm password'
            }),
        }
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive")
        return cleaned_data