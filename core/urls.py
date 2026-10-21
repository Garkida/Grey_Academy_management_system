from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("courses/", views.courses_view, name="courses"),
    path("contact/", views.contact_view, name="contact"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("gallery/", views.gallery_view, name="gallery"),
]
