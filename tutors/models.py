from django.conf import settings
from django.db import models

TUTOR_FIELDS = [
    ("frontend", "Frontend Engineering"),
    ("backend", "Backend Engineering"),
    ("cybersecurity", "Cyber Security"),
    ("data_analysis", "Data Analysis"),
    ("product_design", "Product Design"),
]

class TutorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_profile",
    )

    field = models.CharField(max_length=30, choices=TUTOR_FIELDS)
    photo = models.ImageField(
    upload_to="tutor_photos/%Y/%m/",
    blank=True,
    null=True,
)

    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} — {self.get_field_display()}"


class Lesson(models.Model):
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
