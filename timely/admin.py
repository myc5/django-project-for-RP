from django.contrib import admin

from .models import Clients, Hours, Projects, Vacation, Employees

admin.site.register(Clients)
admin.site.register(Hours)
admin.site.register(Projects)
admin.site.register(Vacation)
admin.site.register(Employees)
