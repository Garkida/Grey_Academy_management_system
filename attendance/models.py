from django.conf import settings
from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    class Method(models.TextChoices):
        WIFI = "wifi", "Academy Wi-Fi"
        GPS = "gps", "Location"
        BOTH = "both", "Wi-Fi and location"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField(default=timezone.localdate)
    checked_in_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=Method.choices)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date"],
                name="one_checkin_per_student_per_day",
            )
        ]
        ordering = ["-date", "-checked_in_at"]

    def __str__(self):
        return f"{self.student} — {self.date}"