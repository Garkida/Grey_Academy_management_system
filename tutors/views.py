from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from attendance.models import Attendance
from payments.models import PendingEnrollment

from .forms import LessonForm, TutorSignupForm
from .models import Lesson, TutorProfile


User = get_user_model()


def signup_view(request):
    if request.method == "POST":
        form = TutorSignupForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                user = User(
                    email=form.cleaned_data["email"],
                    username=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone_number=form.cleaned_data["phone_number"],
                    is_active=True,
                    is_verified=True,
                )
                user.set_password(form.cleaned_data["password1"])
                user.save()

                TutorProfile.objects.create(
                    user=user,
                    field=form.cleaned_data["field"],
                    photo=form.cleaned_data["photo"],
                    bio=form.cleaned_data.get("bio", ""),
                )

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect("tutors:dashboard")
    else:
        form = TutorSignupForm()

    return render(request, "tutors/signup.html", {"form": form})


@login_required
def dashboard_view(request):
    tutor_profile = get_object_or_404(TutorProfile, user=request.user)

    students = PendingEnrollment.objects.filter(assigned_tutor=tutor_profile)
    lessons = Lesson.objects.filter(tutor=tutor_profile)

    active_dashboard_panel = "overview"

    if request.method == "POST":
        form = LessonForm(request.POST)

        if form.is_valid():
            Lesson.objects.create(
                tutor=tutor_profile,
                title=form.cleaned_data["title"],
                video_url=form.cleaned_data["video_url"],
                message=form.cleaned_data.get("message", ""),
            )
            return redirect("tutors:dashboard")
        else:
            active_dashboard_panel = "lessons"
    else:
        form = LessonForm()

    return render(
        request,
        "tutors/dashboard.html",
        {
            "tutor_profile": tutor_profile,
            "students": students,
            "lessons": lessons,
            "form": form,
            "active_dashboard_panel": active_dashboard_panel,
        },
    )


@login_required
def attendance_report_view(request):
    tutor_profile = get_object_or_404(TutorProfile, user=request.user)

    start_date = (
        parse_date(request.GET.get("start", ""))
        or timezone.localdate().replace(day=1)
    )
    end_date = parse_date(request.GET.get("end", "")) or timezone.localdate()
    total_days = (end_date - start_date).days + 1

    students = PendingEnrollment.objects.filter(assigned_tutor=tutor_profile)

    rows = []
    for student in students:
        attended = Attendance.objects.filter(
            student=student.user,
            date__gte=start_date,
            date__lte=end_date,
        ).count()

        percentage = round((attended / total_days) * 100, 1) if total_days else 0

        rows.append(
            {
                "student": student,
                "attended": attended,
                "total_days": total_days,
                "percentage": percentage,
            }
        )

    rows.sort(key=lambda row: row["percentage"], reverse=True)

    return render(
        request,
        "tutors/report.html",
        {
            "rows": rows,
            "start_date": start_date,
            "end_date": end_date,
        },
    )