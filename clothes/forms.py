from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Contact, Testimonial, UserProfile
from django.contrib.auth.models import User

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']

    # Optional: Add custom validation for the fields
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add custom email validation if needed
        return email

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
    password=None

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'height', 'weight', 'body_shape', 'style_preferences']

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError("New passwords must match.")
        return cleaned_data

class AddToCartForm(forms.Form):
    product_id = forms.IntegerField()
    size = forms.CharField(max_length=10)
    quantity = forms.IntegerField(min_value=1)

    # Optional: Add custom validation for the fields
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0')
        return quantity

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'feedback', 'image']
        
    # Optional: Add custom validation for the fields
    def clean_feedback(self):
        feedback = self.cleaned_data.get('feedback')
        if len(feedback) < 10:
            raise forms.ValidationError('Feedback must be at least 10 characters long.')
        return feedback
