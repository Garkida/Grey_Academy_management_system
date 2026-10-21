from rest_framework.permissions import BasePermission

from payments.models import PendingEnrollment


class IsTutor(BasePermission):
    message = "Only tutors can access this endpoint."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "tutor_profile")
        )


class IsVerifiedStudent(BasePermission):
    message = "Only verified Grey Academy students can access this endpoint."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return PendingEnrollment.objects.filter(
            user=request.user,
            payment_status=PendingEnrollment.PaymentStatus.PAID,
            physical_status=PendingEnrollment.PhysicalStatus.VERIFIED,
        ).exists()