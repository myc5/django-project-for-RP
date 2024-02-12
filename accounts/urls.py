from django.urls import path

from .views import SignUpView, send_email, custom_register


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("email/", send_email, name="email"),
    path("custom_register", custom_register, name="custom_register"),
]
