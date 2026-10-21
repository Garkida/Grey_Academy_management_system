import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Attendance
from .util import distance_in_meters, get_client_ip


@login_required
@require_POST
def check_in_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {}

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    today = timezone.localdate()

    if Attendance.objects.filter(student=request.user, date=today).exists():
        return JsonResponse(
            {"status": "already_checked_in", "message": "You already checked in today."}
        )

    client_ip = get_client_ip(request)
    wifi_ok = bool(
        settings.ACADEMY_WIFI_PUBLIC_IP
        and client_ip == settings.ACADEMY_WIFI_PUBLIC_IP
    )

    gps_ok = False
    if latitude is not None and longitude is not None:
        try:
            distance = distance_in_meters(
                float(latitude),
                float(longitude),
                settings.ACADEMY_LATITUDE,
                settings.ACADEMY_LONGITUDE,
            )
            gps_ok = distance <= settings.ACADEMY_CHECKIN_RADIUS_METERS
        except (TypeError, ValueError):
            gps_ok = False

    if not wifi_ok and not gps_ok:
        return JsonResponse(
            {
                "status": "rejected",
                "message": "You must be at the academy, on the academy Wi-Fi, "
                "or with location enabled, to check in.",
            },
            status=403,
        )

    if wifi_ok and gps_ok:
        method = Attendance.Method.BOTH
    elif wifi_ok:
        method = Attendance.Method.WIFI
    else:
        method = Attendance.Method.GPS

    Attendance.objects.create(
        student=request.user,
        date=today,
        method=method,
        ip_address=client_ip,
        latitude=latitude,
        longitude=longitude,
    )

    return JsonResponse({"status": "success", "message": "Attendance marked for today."})

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils.dateparse import parse_date

from payments.models import PendingEnrollment


@user_passes_test(lambda user: user.is_staff)
def attendance_report_view(request):
    start_date = parse_date(request.GET.get("start", "")) or timezone.localdate().replace(day=1)
    end_date = parse_date(request.GET.get("end", "")) or timezone.localdate()

    total_days = (end_date - start_date).days + 1

    enrollments = PendingEnrollment.objects.filter(
        payment_status=PendingEnrollment.PaymentStatus.PAID,
        physical_status=PendingEnrollment.PhysicalStatus.VERIFIED,
        user__isnull=False,
    ).select_related("user")

    rows = []
    for enrollment in enrollments:
        attended = Attendance.objects.filter(
            student=enrollment.user,
            date__gte=start_date,
            date__lte=end_date,
        ).count()

        percentage = round((attended / total_days) * 100, 1) if total_days else 0

        rows.append(
            {
                "name": f"{enrollment.first_name} {enrollment.last_name}",
                "email": enrollment.email,
                "course": enrollment.course_name,
                "attended": attended,
                "total_days": total_days,
                "percentage": percentage,
            }
        )

    rows.sort(key=lambda r: r["percentage"], reverse=True)

    return render(
        request,
        "attendance/report.html",
        {
            "rows": rows,
            "start_date": start_date,
            "end_date": end_date,
        },
    )