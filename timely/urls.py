from django.urls import path

from timely.views import create_view, user_details, client_details, project_details, vacation_details, edit_view, analytics_view, delete_view, vacations_view


urlpatterns = [
    path("create_view/", create_view, name="create_view"),
    path("users/<int:id>", user_details, name="user_details"),
    path("projects/<int:id>", project_details, name="project_details"),
    path("clients/<int:id>", client_details, name="client_details"),
    path("vacations/<int:id>", vacation_details, name="vacation_details"),
    path("logs/<int:id>", edit_view, name="edit_view"),
    path('logs/<int:id>/delete/', delete_view, name="delete_view"),
    path("analytics", analytics_view, name="analytics"),
    path("vacations", vacations_view, name="vacations_view"),
]
