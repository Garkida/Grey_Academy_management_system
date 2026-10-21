from django.urls import path

from . import views

app_name = "tutors"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("attendance/", views.attendance_report_view, name="attendance_report"),
]
