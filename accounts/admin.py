from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# custom Admin form that adds first_name, last_name and e-mail to the first page of user creation (saves a click or two)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password','email')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password1', 'password2', 'email')}
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm

try:
    admin.site.unregister(User)
except admin.site.NotRegistered:
    pass

admin.site.register(User, UserAdmin)

