from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "method", "checked_in_at", "ip_address")
    list_filter = ("method", "date")
    search_fields = ("student__email", "student__first_name", "student__last_name")