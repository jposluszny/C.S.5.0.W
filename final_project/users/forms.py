from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User
from django.forms import ModelForm


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'telefon_number', 'email', 'address', 'born', 'staff_member', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4}),
        }

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}))
    staff_member = forms.BooleanField(label='Staff member', required=False)
    born = forms.DateField(label='Date of birth', widget=forms.DateInput(attrs={'type': 'date'}))


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                  'first_name', 'last_name', 'telefon_number', 'email', 'born', 'address', 'staff_member', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4}),
        }

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}))
    staff_member = forms.BooleanField(label='Staff member', required=False)
    born = forms.DateField(label='Date of birth', widget=forms.DateInput(attrs={'type': 'date'}))
