from django.contrib import admin

from .models import Lesson, TutorProfile


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "field", "created_at")
    list_filter = ("field",)
    search_fields = ("user__email", "user__first_name", "user__last_name")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "tutor", "created_at")
    list_filter = ("tutor",)