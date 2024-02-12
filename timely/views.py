from re import S
from xmlrpc.client import ResponseError
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse, redirect
from django.core.exceptions import ValidationError
from django import forms
from django.contrib import messages
from django.utils.timezone import now
from django.utils.translation import ngettext_lazy
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from .forms import HoursForm, HoursFormNoDate, VacationForm
from .models import Hours, Clients, Projects, Vacation
from django.db.models import Avg, Min, Max, Q, Sum

from django.contrib.auth.admin import User #access the registered users
from django.contrib.auth.decorators import login_required, user_passes_test

from datetime import datetime, date, timedelta
from workalendar.europe import Germany, Greece
import calendar

def get_date_range():
    today = date.today()
    calendar_day =  today.isocalendar()[2] # i.e. weekday=1
    
    if calendar_day == 1:
        past_offset = 0
        future_offset = 6
    if calendar_day == 7:
        past_offset = 6
        future_offset = 0
    else:
        future_offset = 7 - calendar_day
        past_offset = calendar_day - 1
    cw_start_date = today - timedelta(days=past_offset)
    cw_end_date = today + timedelta(days=future_offset)
    lw_start_date = cw_start_date - timedelta(days=7)
    lw_end_date = cw_end_date - timedelta(days=7)
    #return [cw_start_date.strftime("%Y-%m-%d"), cw_end_date.strftime("%Y-%m-%d"), lw_start_date.strftime("%Y-%m-%d"), lw_end_date.strftime("%Y-%m-%d")]
    return [cw_start_date, cw_end_date, lw_start_date, lw_end_date]

todays_date = date.today().strftime("%Y-%m-%d") # move it into the function? only an issue if site loads at like 23:59 and user tries to update at 0:01 or something
this_week = get_date_range()[:2]
last_week = get_date_range()[2:]

# SETTINGS
max_daily_hours_allowed = 12 # Add the allowed time here in hours
backlogging_days_allowed = 2 # Add extra leeways days for the past. I.e. 1 would allow people to log for yesterday, 7 for the past week etc
futurelogging_days_allowed = 1 # Same as above but for future days.

vacation_day_threshhold = 3 # How long a vacation has to be for it to be counted under the vacations page

@login_required
def create_view(request):
    #if request.user.is_superuser:
    #    return HttpResponse("You are logged in as a superuser. If you want to log hours for employees, please use the admin panel instead.")
    form = HoursForm(request.POST or None) 
    u = request.user.username
    past_allowed_date = date.today() - timedelta(days=backlogging_days_allowed)
    future_allowed_date = date.today() + timedelta(days=futurelogging_days_allowed)
    note= None
    emp_hours_cw = Hours.objects.filter(employee__username=u, date__range=this_week).order_by("-date")
    emp_hours_lw = Hours.objects.filter(employee__username=u, date__range=last_week).order_by("-date")
    emp_last = Hours.objects.filter(employee__username=u).last()
    emp_week_total = emp_hours = 0
    emp_hours_today = Hours.objects.filter(employee__username=u, date=date.today())
    for hours in emp_hours_cw:
        emp_week_total += hours.time
    for hours in emp_hours_today:
        emp_hours += hours.time
    print("Base load", emp_week_total, emp_hours)
    if form.is_valid():
        n = form.cleaned_data["name"]
        p = form.cleaned_data["project"]
        t = form.cleaned_data["time"]
        d = form.cleaned_data["date"]
        c = form.cleaned_data["comment"]
        #emp_hours = emp_week_total = 0
        #for hours in emp_hours_today:
        #    emp_hours += hours.time
        if emp_hours + t > max_daily_hours_allowed and (d > past_allowed_date or d < future_allowed_date or d == date.today()):
            
            #for entries in emp_hours_cw:
            #    emp_week_total += entries.time
            #for hours in emp_hours_today:
            #    emp_hours += hours.time
            print(">12h event", emp_week_total, emp_hours)
            return render(request, "create_view.html", {"context": form, "warning": f"You cannot log more than {max_daily_hours_allowed} hours per day. Contact staff if you need help.\n", "emp_hours_cw": emp_hours_cw, "emp_last": emp_last, "cw_start":this_week[0], "cw_end":this_week[1], "lw_start": last_week[0], "lw_end":last_week[1], "emp_week_total":emp_week_total, "emp_hours_lw": emp_hours_lw, "today":date.today(), "phours":prettier_time(emp_week_total), "phours_today":prettier_time(emp_hours)})           
        #print(todays_date, type(todays_date))
        #print(d, type(d))
        #print(u)
        #print(form.cleaned_data)
        # check for duplicate entries
        if Hours.objects.filter(name=n, employee__username=u, project__name=p, date=d).exists(): # username changes to first/last name
            entry = Hours.objects.filter(name=n, employee__username=u, date=d)[0]
            old_t = entry.time # save old time for printing in the view
            entry.time = t # update time
            entry.comment = c # save the comment either way, we don't check for uniqueness here
            entry.save() # after saving update the objects to calculate new weekly/daily hours
            emp_hours_cw = Hours.objects.filter(employee__username=u, date__range=this_week).order_by("-date")
            emp_hours_lw = Hours.objects.filter(employee__username=u, date__range=last_week).order_by("-date")
            emp_hours_today = Hours.objects.filter(employee__username=u, date=date.today())
            emp_last = Hours.objects.filter(employee__username=u).last()
            emp_week_total = emp_hours = 0
            for entries in emp_hours_cw:
                emp_week_total += entries.time
            for hours in emp_hours_today:
                emp_hours += hours.time
            print("Update event", emp_week_total, emp_hours)
            return render(request, "create_view.html", {"context": form, "warning": f"Entry already exists, updating it instead. Hours {old_t} -> {t}).\n", "emp_hours_cw": emp_hours_cw, "emp_last": emp_last, "cw_start":this_week[0], "cw_end":this_week[1], "lw_start": last_week[0], "lw_end":last_week[1], "emp_week_total":emp_week_total, "emp_hours_lw": emp_hours_lw, "today":date.today(), "phours":prettier_time(emp_week_total), "phours_today":prettier_time(emp_hours)})
        if d < past_allowed_date:
            messages.add_message(request, messages.WARNING, f'{todays_date}: User "{request.user.first_name} {request.user.last_name}" tried to log project hours for the past.')
            print("Past event", emp_week_total, emp_hours)
            return render(request, "create_view.html", {"context": form, "warning": "You cannot log project hours for the past. Contact staff to have them fix this for you.", "emp_hours_cw": emp_hours_cw, "emp_last": emp_last, "cw_start":this_week[0], "cw_end":this_week[1], "lw_start": last_week[0], "lw_end":last_week[1], "emp_week_total":emp_week_total, "emp_hours_lw": emp_hours_lw, "today":date.today(), "phours":prettier_time(emp_week_total), "phours_today":prettier_time(emp_hours)})
        elif d > future_allowed_date:
            messages.add_message(request, messages.WARNING, f'{todays_date}: User "{request.user.first_name} {request.user.last_name}" tried to log project hours for the future.')
            print("Future event", emp_week_total, emp_hours)
            return render(request, "create_view.html", {"context": form, "warning": "You cannot log project hours for future days.", "emp_hours_cw": emp_hours_cw, "emp_last": emp_last, "cw_start":this_week[0], "cw_end":this_week[1], "lw_start": last_week[0], "lw_end":last_week[1], "emp_week_total":emp_week_total, "emp_hours_lw": emp_hours_lw, "today":date.today(), "phours":prettier_time(emp_week_total), "phours_today":prettier_time(emp_hours)})
        f = Hours(name=n, project=p, time=t, date=d, comment=c)
        f.save()
        emp_hours_cw = Hours.objects.filter(employee__username=u, date__range=this_week).order_by("-date")
        emp_hours_lw = Hours.objects.filter(employee__username=u, date__range=last_week).order_by("-date")
        emp_last = Hours.objects.filter(employee__username=u).last()
        emp_hours_today = Hours.objects.filter(employee__username=u, date=date.today())
        note = "Time successfully logged."
    else:
        form = HoursForm()
    emp_week_total = emp_hours = 0 # these blocks are added multiple times to update after each entry
    for entries in emp_hours_cw:
        emp_week_total += entries.time
    for hours in emp_hours_today:
        emp_hours += hours.time
    print("Base event 2", emp_week_total, emp_hours)
    return render(request, "create_view.html", {"context": form, "note":note, "emp_hours_cw": emp_hours_cw, "emp_last": emp_last, "cw_start":this_week[0], "cw_end":this_week[1], "lw_start": last_week[0], "lw_end":last_week[1], "emp_week_total":emp_week_total, "emp_hours_lw": emp_hours_lw, "today":date.today(), "phours":prettier_time(emp_week_total), "phours_today":prettier_time(emp_hours)})

def edit_view(request, id):
    context = {}
    obj = get_object_or_404(Hours, id=id)
    
    if request.user.id == obj.employee_id:
        employee_id = obj.employee_id
        if date.today() == obj.date:
            emp_hours_today = Hours.objects.filter(employee_id=employee_id, date=date.today())
            emp_hours = 0
            print(emp_hours_today)
            for hours in emp_hours_today:
                emp_hours += hours.time
            form = HoursFormNoDate(request.POST or None, instance = obj)
            if form.is_valid():
                t = form.cleaned_data["time"]
                print(t, emp_hours)
                if emp_hours + t - hours.time > max_daily_hours_allowed:
                    return HttpResponse(f"You cannot log more than {max_daily_hours_allowed} hours per day. Contact staff if you need help. (You have {max_daily_hours_allowed - emp_hours}h available, the maximum hours you can enter here to get to 12h exactly is: {max_daily_hours_allowed - (emp_hours - hours.time)}h.")
                form.save()
                return redirect("/timely/create_view")
            context["form"] = form
            return render(request, "update_view.html", context)
        note = "You may only edit today's logs."
        return render(request, "403.html", {"note":note})
    note = "You can only edit your own logs."
    return render(request, "403.html", {"note":note})

def delete_view(request, id):
    obj = get_object_or_404(Hours, id=id)
    if request.user.id == obj.employee_id:
        if date.today() == obj.date:
            if request.method == "POST":
                obj.delete()
                return HttpResponseRedirect("/timely/create_view")
            return render(request, "confirm_delete.html", {"object": obj})
        note = "You may only delete today's logs."
        return render(request, "403.html", {"note":note})
    note = "You may only delete your own logs."
    return render(request, "403.html", {"note":note})
    
# Update analytics to use aggregates and user_details; vacation_check should check for pending vacations (like "No vac this year but has count() waiting approval, Link to vacation page "Approve?")
@user_passes_test(lambda u: u.is_superuser)
def analytics_view(request): #
    users = User.objects.all().order_by("username")
    hours = Hours.objects.all()
    projects = Projects.objects.all().order_by("name")
    clients = Clients.objects.all().order_by("name")
    vacations = Vacation.objects.all().order_by("start")
    ongoing_vacs = vacations.filter(start__lte=date.today(), end__gte=date.today())
    upcoming_vacs_next_week = vacations.filter(start__lte=date.today() + timedelta(days=7)).exclude(start__lte=date.today(), end__gte=date.today())
    upcoming_vacs_next_month = vacations.filter(start__lte=date.today() + timedelta(days=30), start__gt=date.today() + timedelta(days=7))
    upcoming_vacs_next_half_year = vacations.filter(start__lte=date.today() + timedelta(days=180), start__gt=date.today() + timedelta(days=30))
    upcoming_vacs_all = vacations.filter(start__gt=date.today())
    context = {"users": users, "clients":clients, "projects":projects,
               "vacations":vacations, "ongoing_vacs":ongoing_vacs, "upcoming_vacs_all":upcoming_vacs_all, "upcoming_vacs_next_week":upcoming_vacs_next_week, "upcoming_vacs_next_month":upcoming_vacs_next_month, "upcoming_vacs_next_half_year": upcoming_vacs_next_half_year,
               }
    return render(request, "analytics.html", context)

@user_passes_test(lambda u: u.is_superuser)
def user_details(request, id):
    emp = get_object_or_404(User, id = id)
    hours = Hours.objects.filter(employee__id=id)
    
    current_year = date.today().year
    adjusted_year = current_year
    current_month = date.today().month # idea: date__gte="year-month-01" .filter date__lt=year-month+1-01, avoids having to deal with leap years and 30/31 day months
    next_month = current_month + 1
    last_month = current_month - 1
    if next_month > 12:
        next_month = 1
        adjust_year += 1
    elif last_month < 1:
        last_month = 12
        adjusted_year -= 1 # only use this for the last month views, don't change year var for any other calculations
        
    # Breaking down the logged hours into time chunks    
    emp_hours_cw = hours.filter(date__range=this_week).order_by("-date") # current week
    emp_hours_lw = hours.filter(date__range=last_week).order_by("-date") # last week
    emp_hours_cm = hours.filter(date__gte=f"{current_year}-{current_month}-{1}").filter(date__lt=f"{adjusted_year}-{next_month}-01").order_by("-date") # current full month
    emp_hours_lm = hours.filter(date__gte=f"{adjusted_year}-{last_month}-{1}").filter(date__lt=f"{current_year}-{current_month}-01").order_by("-date") # last full month
    emp_hours_q1 = hours.filter(date__range=[f"{current_year}-01-01", f"{current_year}-03-31"]).order_by("-date") # first quarter Jan 1 - March 31
    emp_hours_q2 = hours.filter(date__range=[f"{current_year}-04-01", f"{current_year}-06-30"]).order_by("-date") # second quarter April 1 - June 30
    emp_hours_q3 = hours.filter(date__range=[f"{current_year}-07-01", f"{current_year}-09-30"]).order_by("-date") # third quarter Jul 1 - Sept 30
    emp_hours_q4 = hours.filter(date__range=[f"{current_year}-10-01", f"{current_year}-12-31"]).order_by("-date") # fourth quarter Oct 1 - Dec 31
    emp_hours_cy = hours.filter(date__gte=f"{current_year}-01-01").filter(date__lt=f"{current_year+1}-01-01").order_by("-date") # current full year
    emp_hours_ly = hours.filter(date__gte=f"{current_year-1}-01-01").filter(date__lt=f"{current_year}-01-01").order_by("-date") # last full year
    emp_hours_all = hours.order_by("-time", "date") # every single entry ordered by time, desc with date as secondary decider
    emp_last = hours.last()
    
    
    # Summing up all hours for each time chunk
    emp_hours_cw_sum = emp_hours_lw_sum = emp_hours_cm_sum = emp_hours_lm_sum = emp_hours_q1_sum = emp_hours_q2_sum = emp_hours_q3_sum = emp_hours_q4_sum = emp_hours_cy_sum = emp_hours_ly_sum = emp_hours_all_sum = 0
    for hours in emp_hours_cw:
        emp_hours_cw_sum += hours.time
    
    for hours in emp_hours_lw:
        emp_hours_lw_sum += hours.time
        
    for hours in emp_hours_cm:
        emp_hours_cm_sum += hours.time
        
    for hours in emp_hours_lm:
        emp_hours_lm_sum += hours.time
        
    for hours in emp_hours_q1:
        emp_hours_q1_sum += hours.time
        
    for hours in emp_hours_q2:
        emp_hours_q2_sum += hours.time
        
    for hours in emp_hours_q3:
        emp_hours_q3_sum += hours.time
        
    for hours in emp_hours_q4:
        emp_hours_q4_sum += hours.time
        
    for hours in emp_hours_cy:
        emp_hours_cy_sum += hours.time
        
    for hours in emp_hours_ly:
        emp_hours_ly_sum += hours.time
        
    for hours in emp_hours_all:
        emp_hours_all_sum += hours.time
    
    #[0][0] = Project Name | [0][1][1] = Client Name | [0][1][0] = Project hours
    e_h_cm = project_time(emp_hours_cm)
    highest_hours_project_cm_pname = e_h_cm[0][0]
    highest_hours_project_cm_cname = e_h_cm[0][1][1]
    highest_hours_project_cm_time = e_h_cm[0][1][0]
    
    e_h_all = project_time(emp_hours_all)
    highest_hours_project_lt_pname = e_h_all[0][0]
    highest_hours_project_lt_cname = e_h_all[0][1][1]
    highest_hours_project_lt_time = e_h_all[0][1][0]
    
    context = {"emp_hours_cw": emp_hours_cw, "emp_hours_lw":emp_hours_lw, "emp_hours_cm": emp_hours_cm, "emp_hours_lm":emp_hours_lm,
               "emp_hours_cw_sum": emp_hours_cw_sum, "emp_hours_lw_sum":emp_hours_lw_sum, "emp_hours_cm_sum": emp_hours_cm_sum, "emp_hours_lm_sum":emp_hours_lm_sum, 
               "emp_hours_q1":emp_hours_q1, "emp_hours_q2":emp_hours_q2, "emp_hours_q3":emp_hours_q3, "emp_hours_q4":emp_hours_q4, 
               "emp_hours_q1_sum":emp_hours_q1_sum, "emp_hours_q2_sum":emp_hours_q2_sum, "emp_hours_q3_sum":emp_hours_q3_sum, "emp_hours_q4_sum":emp_hours_q4_sum, 
               "emp_hours_cy":emp_hours_cy, "emp_hours_ly":emp_hours_ly, "emp_hours_all":emp_hours_all, "emp_last":emp_last, 
               "emp_hours_cy_sum":emp_hours_cy_sum, "emp_hours_ly_sum":emp_hours_ly_sum, "emp_hours_all_sum":emp_hours_all_sum,
               "emp":emp, "vacation": vacation_info(id),
               "highest_hours_project_cm_pname":highest_hours_project_cm_pname, "highest_hours_project_cm_cname": highest_hours_project_cm_cname, "highest_hours_project_cm_time": highest_hours_project_cm_time,
               "highest_hours_project_lt_pname":highest_hours_project_lt_pname, "highest_hours_project_lt_cname": highest_hours_project_lt_cname, "highest_hours_project_lt_time": highest_hours_project_lt_time
               }
    # Hours.objects.filter(employee_id=5)[0].project.client.name # BMW
    # Hours.objects.filter(employee_id=5)[0].project.name # BMW Project 1
    return render(request, "user_details.html", context)

@user_passes_test(lambda u: u.is_superuser)
def project_details(request, id):
    projects = get_object_or_404(Projects, id = id)
    #project = Projects.objects.filter(employee__id=id)    
    context = {"projects":projects}
    return render(request, "project_details.html", context)

@user_passes_test(lambda u: u.is_superuser)
def client_details(request, id):
    clients = get_object_or_404(Clients, id = id)
    #project = Projects.objects.filter(employee__id=id)    
    context = {"clients":clients}
    return render(request, "client_details.html", context)

#@user_passes_test(lambda u: u.is_superuser)
def vacation_details(request, id):
    vacations = get_object_or_404(Vacation, id = id)
    #project = Projects.objects.filter(employee__id=id)    
    context = {"vacations":vacations}
    return render(request, "vacation_details.html", context)

def vacation_info(id):
    vac = Vacation.objects.filter(employee_id=id)
    emp = User.objects.get(id=id).first_name + " " + User.objects.get(id=id).last_name
    if vac == None:
        return f"{emp} has yet to take a vacation."
    for v in vac:
        if v.start <= date.today() <= v.end:
            return f"{emp} is currently on vacation and will be back on {v.end.strftime('%Y-%m-%d')}."
        elif date.today() < v.start:
            return f"{emp} has their next planned vacation starting at {v.start.strftime('%Y-%m-%d')} until {v.end.strftime('%Y-%m-%d')}."
    return f"{emp} has no upcoming vacations this year."

def prettier_time(hours):
    if hours == 0:
        return "0h"
    hours = str(hours).split(".")
    if hours[0] == "":
        hours[0] = "0"
    if hours[1] == "5":
        hours[1] = "50" # fix 30 mins showing as 3 (using 0.6 below instead of 6 or it will screw with 15 mins (150) and 45 mins (450), so this is simpler to fix)
    phours = f"{hours[0]}h {(float(hours[1])) * 0.6 :.0f}min"
    return phours

def project_time(hours_obj):
    if hours_obj == None:
        return 
    s = {}
    pset = set(s)
    for i in hours_obj:
        pset.add(i.project.name)
    p_dict = {}       
    for item in pset:
        subtotal = 0
        for i in hours_obj.filter(project__name=item):
            subtotal += i.time
        p_dict[item] = (subtotal, i.project.client.name)
    #p_dict_sorted = dict(sorted(p_dict.items(), key=lambda x:x[1], reverse=True)) # sort by highest time (key), desc; result is a list, so dict() it back into a dictionary e: dict turned out to be needed since we split it for the template anyway
    p_dict_sorted = sorted(p_dict.items(), key=lambda x:x[1], reverse=True)
    return p_dict_sorted # Sorted highest to lowest, first entry: [0][0] = Project Name | [0][1][1] = Client Name | [0][1][0] = Project hours

@login_required
def vacations_view(request):
    note = ""
    approved_vacs_this_year, pending_vacs_this_year, vacations, ongoing_vacs, approved_upcoming_vacs_all, approved_upcoming_vacs_next_week, approved_upcoming_vacs_next_month, approved_upcoming_vacs_next_half_year, pending_upcoming_vacs_all, pending_upcoming_vacs_next_week, pending_upcoming_vacs_next_month, pending_upcoming_vacs_next_half_year, past_approved_vacs_all = vacation_list()
    form = VacationForm(request.POST or None) 
    u = request.user.id
    last = Vacation.objects.last()
    if form.is_valid():
        s = form.cleaned_data["start"]
        e = form.cleaned_data["end"]
        print(s, e)
        f = Vacation(employee_id=u, start=s, end=e, status="PENDING")
        #print("New:", f.start, f.end, f.employee.id) 
        #print("Old:", last.start, last.end, last.employee.id)
        #print(bool(f.employee.id != last.employee.id))
        print(bool(f.start > date.today()))
        print(bool(f.start > f.end))
        if f.start < date.today():
            note = "Your vacation start must not lie in the past. Please correct the issue and try again."
            context = {"vacations":vacations, "ongoing_vacs":ongoing_vacs, "approved_upcoming_vacs_all":approved_upcoming_vacs_all, "approved_upcoming_vacs_next_week":approved_upcoming_vacs_next_week, "approved_upcoming_vacs_next_month":approved_upcoming_vacs_next_month, "approved_upcoming_vacs_next_half_year": approved_upcoming_vacs_next_half_year,
               "pending_upcoming_vacs_all":pending_upcoming_vacs_all, "pending_upcoming_vacs_next_week":pending_upcoming_vacs_next_week, "pending_upcoming_vacs_next_month":pending_upcoming_vacs_next_month, "pending_upcoming_vacs_next_half_year": pending_upcoming_vacs_next_half_year,
               "jan_a":approved_vacs_this_year[1], "feb_a":approved_vacs_this_year[2], "mar_a":approved_vacs_this_year[3], "apr_a":approved_vacs_this_year[4], "may_a":approved_vacs_this_year[5], "jun_a":approved_vacs_this_year[6], "jul_a":approved_vacs_this_year[7], "aug_a":approved_vacs_this_year[8], "sep_a":approved_vacs_this_year[9], "oct_a":approved_vacs_this_year[10] , "nov_a": approved_vacs_this_year[11], "dec_a":approved_vacs_this_year[12],
               "jan_p":pending_vacs_this_year[1], "feb_p":pending_vacs_this_year[2], "mar_p":pending_vacs_this_year[3], "apr_p":pending_vacs_this_year[4], "may_p":pending_vacs_this_year[5], "jun_p":pending_vacs_this_year[6], "jul_p":pending_vacs_this_year[7], "aug_p":pending_vacs_this_year[8], "sep_p":pending_vacs_this_year[9], "oct_p":pending_vacs_this_year[10] , "nov_p": pending_vacs_this_year[11], "dec_p":pending_vacs_this_year[12],
               "threshhold": vacation_day_threshhold, "form":form, "note":note,
               }
            return render(request, "vacations_view.html", context)
        if f.start > f.end:
            note = "Your vacation ends before it even starts. Please correct the issue and try again."
            context = {"vacations":vacations, "ongoing_vacs":ongoing_vacs, "approved_upcoming_vacs_all":approved_upcoming_vacs_all, "approved_upcoming_vacs_next_week":approved_upcoming_vacs_next_week, "approved_upcoming_vacs_next_month":approved_upcoming_vacs_next_month, "approved_upcoming_vacs_next_half_year": approved_upcoming_vacs_next_half_year,
               "pending_upcoming_vacs_all":pending_upcoming_vacs_all, "pending_upcoming_vacs_next_week":pending_upcoming_vacs_next_week, "pending_upcoming_vacs_next_month":pending_upcoming_vacs_next_month, "pending_upcoming_vacs_next_half_year": pending_upcoming_vacs_next_half_year,
               "jan_a":approved_vacs_this_year[1], "feb_a":approved_vacs_this_year[2], "mar_a":approved_vacs_this_year[3], "apr_a":approved_vacs_this_year[4], "may_a":approved_vacs_this_year[5], "jun_a":approved_vacs_this_year[6], "jul_a":approved_vacs_this_year[7], "aug_a":approved_vacs_this_year[8], "sep_a":approved_vacs_this_year[9], "oct_a":approved_vacs_this_year[10] , "nov_a": approved_vacs_this_year[11], "dec_a":approved_vacs_this_year[12],
               "jan_p":pending_vacs_this_year[1], "feb_p":pending_vacs_this_year[2], "mar_p":pending_vacs_this_year[3], "apr_p":pending_vacs_this_year[4], "may_p":pending_vacs_this_year[5], "jun_p":pending_vacs_this_year[6], "jul_p":pending_vacs_this_year[7], "aug_p":pending_vacs_this_year[8], "sep_p":pending_vacs_this_year[9], "oct_p":pending_vacs_this_year[10] , "nov_p": pending_vacs_this_year[11], "dec_p":pending_vacs_this_year[12],
               "threshhold": vacation_day_threshhold, "form":form, "note":note,
               }
            return render(request, "vacations_view.html", context)
        if not ((f.start == last.start) and (f.end == last.end) and (f.employee.id == last.employee.id)): #block duplicate entries
            f.save()
            vac_id = f.id
            approved_vacs_this_year, pending_vacs_this_year, vacations, ongoing_vacs, approved_upcoming_vacs_all, approved_upcoming_vacs_next_week, approved_upcoming_vacs_next_month, approved_upcoming_vacs_next_half_year, pending_upcoming_vacs_all, pending_upcoming_vacs_next_week, pending_upcoming_vacs_next_month, pending_upcoming_vacs_next_half_year, past_approved_vacs_all = vacation_list()
            note = "Your request has been entered successfully."
            context = {"vacations":vacations, "ongoing_vacs":ongoing_vacs, "approved_upcoming_vacs_all":approved_upcoming_vacs_all, "approved_upcoming_vacs_next_week":approved_upcoming_vacs_next_week, "approved_upcoming_vacs_next_month":approved_upcoming_vacs_next_month, "approved_upcoming_vacs_next_half_year": approved_upcoming_vacs_next_half_year,
               "pending_upcoming_vacs_all":pending_upcoming_vacs_all, "pending_upcoming_vacs_next_week":pending_upcoming_vacs_next_week, "pending_upcoming_vacs_next_month":pending_upcoming_vacs_next_month, "pending_upcoming_vacs_next_half_year": pending_upcoming_vacs_next_half_year,
               "jan_a":approved_vacs_this_year[1], "feb_a":approved_vacs_this_year[2], "mar_a":approved_vacs_this_year[3], "apr_a":approved_vacs_this_year[4], "may_a":approved_vacs_this_year[5], "jun_a":approved_vacs_this_year[6], "jul_a":approved_vacs_this_year[7], "aug_a":approved_vacs_this_year[8], "sep_a":approved_vacs_this_year[9], "oct_a":approved_vacs_this_year[10] , "nov_a": approved_vacs_this_year[11], "dec_a":approved_vacs_this_year[12],
               "jan_p":pending_vacs_this_year[1], "feb_p":pending_vacs_this_year[2], "mar_p":pending_vacs_this_year[3], "apr_p":pending_vacs_this_year[4], "may_p":pending_vacs_this_year[5], "jun_p":pending_vacs_this_year[6], "jul_p":pending_vacs_this_year[7], "aug_p":pending_vacs_this_year[8], "sep_p":pending_vacs_this_year[9], "oct_p":pending_vacs_this_year[10] , "nov_p": pending_vacs_this_year[11], "dec_p":pending_vacs_this_year[12],
               "threshhold": vacation_day_threshhold, "form":form, "note":note, "past_approved_vacs_all":past_approved_vacs_all, "vac_id":vac_id,
               }
            return render(request, "vacations_view.html", context)
        note = "You already requested this vacation."
        context = {"vacations":vacations, "ongoing_vacs":ongoing_vacs, "approved_upcoming_vacs_all":approved_upcoming_vacs_all, "approved_upcoming_vacs_next_week":approved_upcoming_vacs_next_week, "approved_upcoming_vacs_next_month":approved_upcoming_vacs_next_month, "approved_upcoming_vacs_next_half_year": approved_upcoming_vacs_next_half_year,
               "pending_upcoming_vacs_all":pending_upcoming_vacs_all, "pending_upcoming_vacs_next_week":pending_upcoming_vacs_next_week, "pending_upcoming_vacs_next_month":pending_upcoming_vacs_next_month, "pending_upcoming_vacs_next_half_year": pending_upcoming_vacs_next_half_year,
               "jan_a":approved_vacs_this_year[1], "feb_a":approved_vacs_this_year[2], "mar_a":approved_vacs_this_year[3], "apr_a":approved_vacs_this_year[4], "may_a":approved_vacs_this_year[5], "jun_a":approved_vacs_this_year[6], "jul_a":approved_vacs_this_year[7], "aug_a":approved_vacs_this_year[8], "sep_a":approved_vacs_this_year[9], "oct_a":approved_vacs_this_year[10] , "nov_a": approved_vacs_this_year[11], "dec_a":approved_vacs_this_year[12],
               "jan_p":pending_vacs_this_year[1], "feb_p":pending_vacs_this_year[2], "mar_p":pending_vacs_this_year[3], "apr_p":pending_vacs_this_year[4], "may_p":pending_vacs_this_year[5], "jun_p":pending_vacs_this_year[6], "jul_p":pending_vacs_this_year[7], "aug_p":pending_vacs_this_year[8], "sep_p":pending_vacs_this_year[9], "oct_p":pending_vacs_this_year[10] , "nov_p": pending_vacs_this_year[11], "dec_p":pending_vacs_this_year[12],
               "threshhold": vacation_day_threshhold, "form":form, "note":note, "past_approved_vacs_all":past_approved_vacs_all
               }
        return render(request, "vacations_view.html", context)
    else:
        form = VacationForm()
    context = {"vacations":vacations, "ongoing_vacs":ongoing_vacs, "approved_upcoming_vacs_all":approved_upcoming_vacs_all, "approved_upcoming_vacs_next_week":approved_upcoming_vacs_next_week, "approved_upcoming_vacs_next_month":approved_upcoming_vacs_next_month, "approved_upcoming_vacs_next_half_year": approved_upcoming_vacs_next_half_year,
               "pending_upcoming_vacs_all":pending_upcoming_vacs_all, "pending_upcoming_vacs_next_week":pending_upcoming_vacs_next_week, "pending_upcoming_vacs_next_month":pending_upcoming_vacs_next_month, "pending_upcoming_vacs_next_half_year": pending_upcoming_vacs_next_half_year,
               "jan_a":approved_vacs_this_year[1], "feb_a":approved_vacs_this_year[2], "mar_a":approved_vacs_this_year[3], "apr_a":approved_vacs_this_year[4], "may_a":approved_vacs_this_year[5], "jun_a":approved_vacs_this_year[6], "jul_a":approved_vacs_this_year[7], "aug_a":approved_vacs_this_year[8], "sep_a":approved_vacs_this_year[9], "oct_a":approved_vacs_this_year[10] , "nov_a": approved_vacs_this_year[11], "dec_a":approved_vacs_this_year[12],
               "jan_p":pending_vacs_this_year[1], "feb_p":pending_vacs_this_year[2], "mar_p":pending_vacs_this_year[3], "apr_p":pending_vacs_this_year[4], "may_p":pending_vacs_this_year[5], "jun_p":pending_vacs_this_year[6], "jul_p":pending_vacs_this_year[7], "aug_p":pending_vacs_this_year[8], "sep_p":pending_vacs_this_year[9], "oct_p":pending_vacs_this_year[10] , "nov_p": pending_vacs_this_year[11], "dec_p":pending_vacs_this_year[12],
               "threshhold": vacation_day_threshhold, "form":form, "note":note,"past_approved_vacs_all":past_approved_vacs_all
               }
    
    return render(request, "vacations_view.html", context)

def create_vacation(request, id):
    form = VacationForm(request.POST or None) 
    u = request.user.username
    vacations = Vacation.objects.filter(employee__username=u, date__range=this_week).order_by("-date")
    emp_hours_lw = Hours.objects.filter(employee__username=u, date__range=last_week).order_by("-date")
    emp_last = Hours.objects.filter(employee__username=u).last()
    emp_week_total = emp_hours = 0
    emp_hours_today = Hours.objects.filter(employee__username=u, date=date.today())
    if form.is_valid():
        s = form.cleaned_data["start"]
        e = form.cleaned_data["end"]
        if Hours.objects.filter(name=n, employee__username=u, project__name=p, date=d).exists(): # username changes to first/last name
            entry = Hours.objects.filter(name=n, employee__username=u, date=d)[0]
            old_t = entry.time # save old time for printing in the view
            entry.time = t # update time
            entry.comment = c # save the comment either way, we don't check for uniqueness here
            entry.save() # after saving update the objects to calculate new weekly/daily hours
            emp_hours_cw = Hours.objects.filter(employee__username=u, date__range=this_week).order_by("-date")
            emp_hours_lw = Hours.objects.filter(employee__username=u, date__range=last_week).order_by("-date")
            emp_hours_today = Hours.objects.filter(employee__username=u, date=date.today())
            emp_last = Hours.objects.filter(employee__username=u).last()
        f = Hours(name=n, project=p, time=t, date=d, comment=c)
        f.save()
        note = "Time successfully logged."
    else:
        form = VacationForm()
    context = {}
    return render(request, "create_view.html", {})

def vacation_list():
    vacations = Vacation.objects.all().order_by("start")
    ongoing_vacs = vacations.filter(start__lte=date.today(), end__gte=date.today(), status="APPROVED")
    approved_upcoming_vacs_next_week = vacations.filter(status="APPROVED", start__range=[date.today() + timedelta(days=1), date.today() + timedelta(days=7)])
    approved_upcoming_vacs_next_month = vacations.filter(status="APPROVED", start__range=[date.today() + timedelta(days=8), date.today() + timedelta(days=31)])
    approved_upcoming_vacs_next_half_year = vacations.filter(status="APPROVED", start__range=[date.today() + timedelta(days=32), date.today() + timedelta(days=183)])
    approved_upcoming_vacs_all = vacations.filter(status="APPROVED", start__gt=date.today())
    pending_upcoming_vacs_next_week = vacations.filter(status="PENDING", start__range=[date.today() + timedelta(days=1), date.today() + timedelta(days=7)])
    pending_upcoming_vacs_next_month = vacations.filter(status="PENDING", start__range=[date.today() + timedelta(days=8), date.today() + timedelta(days=31)])
    pending_upcoming_vacs_next_half_year = vacations.filter(status="PENDING", start__range=[date.today() + timedelta(days=32), date.today() + timedelta(days=183)])
    pending_upcoming_vacs_all = vacations.filter(status="PENDING", start__gt=date.today())
    
    current_year = date.today().year
    past_approved_vacs_all = vacations.filter(status="APPROVED", start__gte=f"{current_year-1}-11-01", end__lt=date.today())
    
    approved_vacs_this_year = {}
    pending_vacs_this_year = {}
    
    app_count = pen_count = 0
    
    for i in range(1, 13):
        if i == 12:
            app = vacations.filter(status="APPROVED", start__gte = f"{current_year}-12-01", start__lte = f"{current_year}-12-31")
            for vac in app:
                if (vac.end - vac.start).days >= vacation_day_threshhold:
                    app_count += 1
            approved_vacs_this_year[i] = app_count
            app_count = 0
            pen = vacations.filter(status="PENDING", start__gte = f"{current_year}-12-01", start__lte = f"{current_year}-12-31")
            for vac in pen:
                if (vac.end - vac.start).days >= vacation_day_threshhold:
                    pen_count += 1
            pending_vacs_this_year[i] = pen_count
            pen_count = 0
        else:
            app = vacations.filter(status="APPROVED", start__gte = f"{current_year}-{i}-01", start__lt = f"{current_year}-{i+1}-01")
            for vac in app:
                if (vac.end - vac.start).days >=vacation_day_threshhold:
                    app_count += 1
            approved_vacs_this_year[i] = app_count
            app_count = 0
            pen = vacations.filter(status="PENDING", start__gte = f"{current_year}-{i}-01", start__lt = f"{current_year}-{i+1}-01")
            for vac in pen:
                if (vac.end - vac.start).days >= vacation_day_threshhold:
                    pen_count += 1
            pending_vacs_this_year[i] = pen_count
            pen_count = 0
    return approved_vacs_this_year, pending_vacs_this_year, vacations, ongoing_vacs, approved_upcoming_vacs_all, approved_upcoming_vacs_next_week, approved_upcoming_vacs_next_month, approved_upcoming_vacs_next_half_year, pending_upcoming_vacs_all, pending_upcoming_vacs_next_week, pending_upcoming_vacs_next_month, pending_upcoming_vacs_next_half_year, past_approved_vacs_all

