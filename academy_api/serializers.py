from rest_framework import serializers

from attendance.models import Attendance
from payments.models import PendingEnrollment
from tutors.models import Lesson, TutorProfile


class CourseSerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    tagline = serializers.CharField()
    blurb = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField())
    duration = serializers.CharField()


class TutorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    field = serializers.SerializerMethodField()
    photo = serializers.ImageField(read_only=True)

    class Meta:
        model = TutorProfile
        fields = ["name", "field", "photo", "bio"]

    def get_name(self, tutor):
        return tutor.user.get_full_name() or tutor.user.email

    def get_field(self, tutor):
        return tutor.get_field_display()


class AttendanceSerializer(serializers.ModelSerializer):
    method = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["date", "checked_in_at", "method"]

    def get_method(self, attendance):
        return attendance.get_method_display()


class AssignedStudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    passport_photo = serializers.ImageField(read_only=True)

    class Meta:
        model = PendingEnrollment
        fields = [
            "public_id",
            "name",
            "course_name",
            "phone_number",
            "email",
            "passport_photo",
        ]

    def get_name(self, student):
        return f"{student.first_name} {student.last_name}"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "message", "created_at"]
        read_only_fields = ["id", "created_at"]