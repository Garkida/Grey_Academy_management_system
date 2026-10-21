from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("check-in/", views.check_in_view, name="check_in"),
    path("report/", views.attendance_report_view, name="attendance_report"),
]