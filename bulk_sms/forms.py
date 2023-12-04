from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserProfileForm(UserCreationForm):
    staff_number = forms.CharField(max_length=20)
    full_name = forms.CharField(max_length=255)
    department = forms.CharField(max_length=100)
    station = forms.CharField(max_length=100)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = UserProfile
        fields = ('staff_number', 'full_name', 'department', 'station', 'role', 'password1', 'password2')
