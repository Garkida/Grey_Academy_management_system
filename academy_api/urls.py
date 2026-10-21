from django.urls import path

from . import views

app_name = "academy_api"

urlpatterns = [
    path("courses/", views.CourseListAPIView.as_view(), name="courses"),
    path("tutors/", views.TutorListAPIView.as_view(), name="tutors"),
    path(
        "my-attendance/",
        views.MyAttendanceListAPIView.as_view(),
        name="my_attendance",
    ),
    path(
        "tutor/students/",
        views.TutorStudentListAPIView.as_view(),
        name="tutor_students",
    ),
    path(
        "tutor/lessons/",
        views.TutorLessonListCreateAPIView.as_view(),
        name="tutor_lessons",
    ),
]