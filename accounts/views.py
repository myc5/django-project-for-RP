from pyexpat import model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.admin import User #access the registered users
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.core.exceptions import ValidationError
from django import forms

allowed_email_domains = ["rapidproto.gr", "rapidproto.de"]


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
      
    
def send_email(request):
    subject = 'Welcome to My Site'
    message = 'Thank you for creating an account!'
    from_email = 'admin@mysite.com'
    recipient_list = [request.user.email]
    send_mail(subject, message, from_email, recipient_list)

def custom_register(request):
    note = ""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["email"].split("@")[1] in allowed_email_domains:
                form.save()
                return redirect("login")
            else:
                note = "E-Mail must be part of the Rapidproto domain!"
    else:
        form = RegisterForm()
    
    return render(request, "custom_register.html", {"form": form, "note": note})

