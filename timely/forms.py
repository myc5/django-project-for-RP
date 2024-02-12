from django import forms
from timely.models import Clients, Hours, Vacation
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from datetime import date

class HoursForm(forms.ModelForm):
    
    class Meta:
        model = Hours
        #fields = "__all__"

        # determine which fields to show in the form (in this case "__all__ would have done the trick)
        fields = [
            "name",
            "project",
            "time",
            "date",
            "comment",
        ]
        
        # rename the labels in the html form only
        labels = {
            "name": "Description"
            }

        
class HoursFormNoDate(forms.ModelForm):
    
    class Meta:
        model = Hours
        #fields = "__all__"

        # determine which fields to show in the form (in this case "__all__ would have done the trick)
        fields = [
            "name",
            "project",
            "time",
            "comment",
        ]
        
        # rename the labels in the html form only
        labels = {
            "name": "Description"
            }

        


class DetailsForm(forms.ModelForm):
    
    class Meta:
        model = Hours
        #fields = "__all__"

        # determine which fields to show in the form (in this case "__all__ would have done the trick)
        fields = [
            "name",
            "project",
            "time",
            "date",
            "comment",
        ]
        
        # rename the labels in the html form only
        labels = {
            "name": "Description"
            }
        
        
class VacationForm(forms.ModelForm):
    
    class Meta:
        model = Vacation
        
        fields = ["start",
                  "end",
                  ]
        widgets = {
            "start": forms.SelectDateWidget(),
            "end": forms.SelectDateWidget(),
        }