from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import Attendance
from core.views import COURSE_TRACKS
from payments.models import PendingEnrollment
from tutors.models import Lesson, TutorProfile

from .permissions import IsTutor, IsVerifiedStudent
from .serializers import (
    AssignedStudentSerializer,
    AttendanceSerializer,
    CourseSerializer,
    LessonSerializer,
    TutorSerializer,
)


class CourseListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = CourseSerializer(COURSE_TRACKS, many=True)
        return Response(serializer.data)


class TutorListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TutorSerializer

    def get_queryset(self):
        return TutorProfile.objects.select_related("user").order_by(
            "user__first_name",
            "user__last_name",
        )


class MyAttendanceListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVerifiedStudent]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return Attendance.objects.filter(
            student=self.request.user
        ).order_by("-date", "-checked_in_at")


class TutorStudentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTutor]
    serializer_class = AssignedStudentSerializer

    def get_queryset(self):
        return PendingEnrollment.objects.filter(
            assigned_tutor=self.request.user.tutor_profile
        ).select_related("user").order_by("first_name", "last_name")


class TutorLessonListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTutor]
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(
            tutor=self.request.user.tutor_profile
        )

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user.tutor_profile)