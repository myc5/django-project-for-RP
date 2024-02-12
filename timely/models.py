from msilib.text import tables
from re import S
from token import COMMENT
from webbrowser import get
from django.db import models
import datetime
from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django_currentuser.middleware import (get_current_user, get_current_authenticated_user)
from django_currentuser.db.models import CurrentUserField
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext as _
from workalendar.europe import Germany, Greece

def holidays_germany(date):
    if date.day == 31 and date.month == 10: # Reformationstag
        return 1 
    if Germany().is_working_day(date):
        return 1
    else:
        return 0
    
def holidays_greece(date): # it is possible to split this into districts by checking employee offices, but is it worth the admin work?
    if Greece().is_working_day(date):
        return 1
    else:
        return 0

# returns each day between start and end (datetime format) to be used later
def date_range(start, end):
    for i in range(int((end - start).days)+1):
        yield start + timedelta(i)

def vacation_days(email, start, end):
    count = 0
    for days in date_range(start, end):
        if email.split("@")[1] == "rapidproto.de":
            count += holidays_germany(days)         
        elif email.split("@")[1] == "rapidproto.gr":
            count += holidays_greece(days)   
    return count



   
class Clients(models.Model):
    name = models.CharField(max_length=200, unique=True)
    
    class Meta:
        verbose_name_plural = "Clients"
    
    def __str__(self):
        return self.name
    
past_dates_not_allowed = True
        
class Hours(models.Model):
    TIME = (
        (0.25, "15 mins"),
        (0.50, "30 mins"),
        (0.75, "45 mins"),
        (1.00, "1h"),
        (1.25, "1h 15 mins"),
        (1.50, "1h 30 mins"),
        (1.75, "1h 45 mins"),
        (2.00, "2h"),
        (2.25, "2h 15 mins"),
        (2.50, "2h 30 mins"),
        (2.75, "2h 45 mins"),
        (3.00, "3h"),
        (3.25, "3h 15 mins"),
        (3.50, "3h 30 mins"),
        (3.75, "3h 45 mins"),
        (4.00, "4h"),
        (4.25, "4h 15 mins"),
        (4.50, "4h 30 mins"),
        (4.75, "4h 45 mins"),
        (5.00, "5h"),
        (6.25, "6h 15 mins"),
        (6.50, "6h 30 mins"),
        (6.75, "6h 45 mins"),
        (7.00, "7h"),
        (7.25, "7h 15 mins"),
        (7.50, "7h 30 mins"),
        (7.75, "7h 45 mins"),
        (8.00, "8h"),
        (8.25, "8h 15 mins"),
        (8.50, "8h 30 mins"),
        (8.75, "8h 45 mins"),
        (9.00, "9h"),
        (9.25, "9h 15 mins"),
        (9.50, "9h 30 mins"),
        (9.75, "9h 45 mins"),
        (10.00, "10h"),
        (10.25, "10h 15 mins"),
        (10.50, "10h 30 mins"),
        (10.75, "10h 45 mins"),
        (11.00, "11h"),
        (11.25, "11h 15 mins"),
        (11.50, "11h 30 mins"),
        (11.75, "11h 45 mins"),
        (12.00, "12h"),
        )
    name = models.CharField(max_length=200)
    employee = CurrentUserField()
    project = models.ForeignKey("Projects", on_delete=models.RESTRICT)
    time = models.FloatField(choices=TIME)
    date = models.DateField(default=now(), max_length=12)
    comment = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(_("DateTime"), auto_now_add=True)
    
    # delete this in the final version
    def Date_validation(value):
        #if value < datetime.date.today():
        if False:
           raise ValidationError("The date cannot be in the past. Contact the admin to have this added manually for you.")
    date = models.DateField(default=datetime.date.today, validators=[Date_validation])
    
    class Meta:
        verbose_name_plural = "Hours"
    
    def __str__(self):
        date_name_desc_time_proj = str(self.date) + " - " + self.employee.first_name + " " + self.employee.last_name + " - " + self.project.name + " - " + self.name + " - " + str(self.time)+ "h"
        return date_name_desc_time_proj

class Projects(models.Model):
    name = models.CharField(max_length=200, unique=True)
    client = models.ForeignKey("Clients", on_delete=models.RESTRICT)    
    
    class Meta:
        verbose_name_plural = "Projects"
        
    def __str__(self):
        return self.name
    
class Vacation(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    start = models.DateField()
    end = models.DateField()
    name = "Vacation"
    #approved = models.BooleanField(default=False)
    STATUS_CHOICES = (
        ("APPROVED", "Approved"),
        ("PENDING", "Pending"),
        ("DENIED", "Denied"),
        
        )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    days = models.IntegerField(blank=True, verbose_name="Vacation Days (do not touch, gets auto-calculated)")
    
    def save(self, *args, **kwargs):
            
        self.days = vacation_days(self.employee.email, self.start, self.end)
        super(Vacation, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.status}: {str(self.start)} to {str(self.end)} - {self.employee.first_name} {self.employee.last_name} | {self.days} days"
    
class Employees(models.Model):
    OFFICE_CHOICES = (
        ("GERMANY", "Germany"),
        ("GR 1", "GR Office 1"),
        ("GR 2", "GR Office 2"),
        )
    user = models.OneToOneField(User, on_delete=models.RESTRICT)
    fullname = models.CharField(max_length=200, blank=True, default="This gets autofilled, do not touch it please")
    special_permissions = models.BooleanField(default=False)
    office = models.CharField(max_length =10, choices=OFFICE_CHOICES, default="GERMANY", name="office")
    notes = models.CharField(max_length = 200, blank=True)
    
    class Meta:
        verbose_name_plural = "Employees"
        
    def save(self, *args, **kwargs):
        self.fullname = f"{self.user.first_name} {self.user.last_name}"
        super(Employees, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Special Permissions: {self.special_permissions} - Notes: {self.notes}"