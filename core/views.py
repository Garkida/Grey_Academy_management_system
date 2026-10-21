from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from payments.models import PendingEnrollment
from tutors.models import TutorProfile
from attendance.models import Attendance


# Course track data shown on the homepage and /courses page.
# Kept simple as a plain list for now — move this to a model later if you
# want tutors to be able to edit tracks from the admin.
COURSE_TRACKS = [
    {
        "key": "frontend",
        "name": "Frontend Engineering",
        "tagline": "Interfaces people love",
        "blurb": "Build fast, accessible, beautiful web interfaces with HTML, CSS, JavaScript and modern React.",
        "skills": ["HTML & CSS", "JavaScript", "React", "UI Systems"],
        "duration": "16 weeks",
    },
    {
        "key": "backend",
        "name": "Backend Engineering",
        "tagline": "The engine room",
        "blurb": "Design APIs, model data and ship secure, scalable server systems that power real products.",
        "skills": ["APIs", "Databases", "Auth", "Cloud Deploys"],
        "duration": "18 weeks",
    },
    {
        "key": "cybersecurity",
        "name": "Cyber Security",
        "tagline": "Defend everything",
        "blurb": "Learn threat modelling, network defence, ethical hacking and incident response from the ground up.",
        "skills": ["Networks", "Pen Testing", "Forensics", "Blue Team"],
        "duration": "20 weeks",
    },
    {
        "key": "data_analysis",
        "name": "Data Analysis",
        "tagline": "Answers inside the numbers",
        "blurb": "Turn messy data into decisions using spreadsheets, SQL, Python and clear visual storytelling.",
        "skills": ["SQL", "Python", "Visualisation", "Reporting"],
        "duration": "14 weeks",
    },
    {
        "key": "product_design",
        "name": "Product Design",
        "tagline": "Design products people choose",
        "blurb": "Research user needs, shape clear product experiences and create interfaces that solve real problems.",
        "skills": ["UX Research", "Wireframing", "Figma", "Prototyping"],
        "duration": "16 weeks",
    },
]

STATS = [
    {"value": "5", "label": "Specialist tracks"},
    {"value": "1:12", "label": "Tutor to student ratio"},
    {"value": "92%", "label": "Project completion"},
    {"value": "24/7", "label": "Learning portal access"},
]


def home_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "tutor_profile"):
            return redirect("tutors:dashboard")
        return redirect("core:dashboard")
    return render(request, "core/home.html", {"tracks": COURSE_TRACKS, "stats": STATS})


def about_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "tutor_profile"):
            return redirect("tutors:dashboard")
        return redirect("core:dashboard")
    return render(request, "core/about.html")


def courses_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "tutor_profile"):
            return redirect("tutors:dashboard")
        return redirect("core:dashboard")
    return render(request, "core/courses.html", {"tracks": COURSE_TRACKS})


def contact_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "tutor_profile"):
            return redirect("tutors:dashboard")
        return redirect("core:dashboard")
    return render(request, "core/contact.html")


def gallery_view(request):
    students = PendingEnrollment.objects.order_by("-created_at")
    tutors = TutorProfile.objects.select_related("user").order_by(
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    return render(
        request,
        "core/gallery.html",
        {"students": students, "tutors": tutors},
    )



@login_required
def dashboard_view(request):
    if hasattr(request.user, "tutor_profile"):
        return redirect("tutors:dashboard")

    enrollment = (
        PendingEnrollment.objects
        .select_related("assigned_tutor__user")
        .filter(
            user=request.user,
            payment_status=PendingEnrollment.PaymentStatus.PAID,
        )
        .order_by("-created_at")
        .first()
    )

    if not enrollment:
        messages.info(
            request,
            "Choose a student type and complete payment to begin registration.",
        )
        return redirect("payments:get_started")

    if enrollment.physical_status != PendingEnrollment.PhysicalStatus.VERIFIED:
        messages.info(
            request,
            "Your dashboard will be available after physical verification at the institute.",
        )
        return redirect("payments:registration_documents")

    tutor = enrollment.assigned_tutor
    lessons = tutor.lessons.all() if tutor else []
    attendance_records = Attendance.objects.filter(
        student=request.user
    ).order_by("-date", "-checked_in_at")

    return render(
        request,
        "core/dashboard.html",
        {
            "enrollment": enrollment,
            "tutor": tutor,
            "lessons": lessons,
            "attendance_records": attendance_records,
        },
    )
