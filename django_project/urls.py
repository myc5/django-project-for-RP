from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from accounts.views import send_email

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  
    path("accounts/", include("django.contrib.auth.urls")), # provides login, logout, password_change/reset_done/confirm_complete urls
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("timely/", include("timely.urls")),
]
