from django.db import models
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.
def setup_token_expiry():
    return timezone.now() + timedelta(hours=48)


class PendingEnrollment(models.Model):
    class StudentType(models.TextChoices):
        ACADEMY = "academy", "Grey Academy Student"
        SIWES = "siwes", "SIWES Student"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending payment"
        PAID = "paid", "Payment confirmed"
        FAILED = "failed", "Payment failed"

    class PhysicalStatus(models.TextChoices):
        AWAITING = "awaiting", "Awaiting physical verification"
        VERIFIED = "verified", "Physically verified"
        REJECTED = "rejected", "Verification rejected"

    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    student_type = models.CharField(
        max_length=10,
        choices=StudentType.choices,
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    course_key = models.CharField(max_length=30)
    course_name = models.CharField(max_length=100)
    other_course_name = models.CharField(max_length=150, blank=True)

    institution_name = models.CharField(max_length=200, blank=True)
    course_of_study = models.CharField(max_length=200, blank=True)
    matric_number = models.CharField(max_length=100, blank=True)

    school_application_letter = models.FileField(
        upload_to="siwes_letters/%Y/%m/",
        blank=True,
        null=True,
    )

    passport_photo = models.ImageField(
        upload_to="passport_photos/%Y/%m/",
    )

    amount = models.PositiveIntegerField(
        help_text="Amount in naira."
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    paid_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    registration_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
    )

    account_setup_token = models.UUIDField(
        unique=True,
        blank=True,
        null=True,
    )
    setup_token_expires_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="enrollments",
    )
    account_completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    physical_status = models.CharField(
        max_length=10,
        choices=PhysicalStatus.choices,
        default=PhysicalStatus.AWAITING,
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="physically_verified_enrollments",
    )
    verified_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} — {self.course_name}"

    assigned_tutor = models.ForeignKey(
        "tutors.TutorProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="students",
    )


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    pending_enrollment = models.ForeignKey(
        PendingEnrollment,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    provider = models.CharField(max_length=20, default="paystack")
    reference = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField(
        help_text="Amount in naira."
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    provider_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} — {self.status}"

