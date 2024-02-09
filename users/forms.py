from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email Address', max_length=200)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
