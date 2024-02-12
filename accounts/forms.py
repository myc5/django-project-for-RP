from django import forms
from django.contrib.auth.admin import User, UserCreationForm
from django.core.exceptions import ValidationError

allowed_email_domains = ["rapidproto.gr", "rapidproto.de"]

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        #fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

