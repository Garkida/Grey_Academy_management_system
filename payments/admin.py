from django.contrib import admin
from django.utils import timezone

from .models import Payment, PendingEnrollment


@admin.action(description="Mark selected students as physically verified")
def mark_physically_verified(modeladmin, request, queryset):
    queryset.filter(
        payment_status=PendingEnrollment.PaymentStatus.PAID
    ).update(
        physical_status=PendingEnrollment.PhysicalStatus.VERIFIED,
        verified_by=request.user,
        verified_at=timezone.now(),
    )


@admin.register(PendingEnrollment)
class PendingEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "registration_number",
        "email",
        "student_type",
        "course_name",
        "amount",
        "payment_status",
        "physical_status",
         "assigned_tutor",
    )
    list_filter = (
        "student_type",
        "payment_status",
        "physical_status",
         "assigned_tutor",
    )
    search_fields = (
        "registration_number",
        "email",
        "matric_number",
        "phone_number",
    )
    actions = [mark_physically_verified]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "pending_enrollment",
        "amount",
        "status",
        "paid_at",
    )
    list_filter = ("status", "provider")
    search_fields = ("reference", "pending_enrollment__email")