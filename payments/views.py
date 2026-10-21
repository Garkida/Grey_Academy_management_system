import hashlib
import hmac
import json
import uuid

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from datetime import timedelta



import os
from pathlib import Path
from urllib.parse import urlparse

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from xhtml2pdf.config.resources import ResourceAccessPolicy

from .catalog import (
    ACADEMY_COURSES,
    SIWES_COURSES,
    get_price,
)
from .forms import (
    AccountSetupForm,
    GreyAcademyRegistrationForm,
    SIWESRegistrationForm,
)
from .models import Payment, PendingEnrollment

User = get_user_model()

PDF_RESOURCE_POLICY = ResourceAccessPolicy(
    base_dir=Path(settings.BASE_DIR / "static"),
    extra_roots=(Path(settings.MEDIA_ROOT),),
)


def pdf_link_callback(uri, rel):
    path = urlparse(uri).path

    if path.startswith(settings.STATIC_URL):
        relative_path = path.removeprefix(settings.STATIC_URL)
        result = finders.find(relative_path)

        if isinstance(result, (list, tuple)):
            result = result[0]

        if result:
            return os.path.realpath(result)

    if path.startswith(settings.MEDIA_URL):
        relative_path = path.removeprefix(settings.MEDIA_URL)
        return os.path.join(settings.MEDIA_ROOT, relative_path)

    return uri

def get_started_view(request):
    return render(request, "payments/get_started.html")


def registration_view(request, student_type):
    if student_type == PendingEnrollment.StudentType.ACADEMY:
        form_class = GreyAcademyRegistrationForm
        course_catalog = ACADEMY_COURSES
    elif student_type == PendingEnrollment.StudentType.SIWES:
        form_class = SIWESRegistrationForm
        course_catalog = SIWES_COURSES
    else:
        messages.error(request, "Unknown student type.")
        return redirect("payments:get_started")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student_type = student_type
            enrollment.amount = get_price(student_type)

            selected_course = form.cleaned_data["course_key"]
            enrollment.course_key = selected_course

            if selected_course == "other":
                enrollment.course_name = form.cleaned_data[
                    "other_course_name"
                ]
            else:
                enrollment.course_name = course_catalog[selected_course]

            enrollment.save()

            return redirect(
                "payments:payment_review",
                public_id=enrollment.public_id,
            )
    else:
        form = form_class()

    return render(
        request,
        "payments/registration_form.html",
        {
            "form": form,
            "student_type": student_type,
            "amount": get_price(student_type),
        },
    )


def payment_review_view(request, public_id):
    enrollment = get_object_or_404(
        PendingEnrollment,
        public_id=public_id,
    )

    if enrollment.payment_status == PendingEnrollment.PaymentStatus.PAID:
        return render(
            request,
            "payments/payment_success.html",
            {"enrollment": enrollment},
        )

    return render(
        request,
        "payments/payment_review.html",
        {"enrollment": enrollment},
    )


def paystack_headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


@require_POST
def start_payment_view(request, public_id):
    enrollment = get_object_or_404(
        PendingEnrollment,
        public_id=public_id,
    )

    if enrollment.payment_status == PendingEnrollment.PaymentStatus.PAID:
        return redirect(
            "payments:payment_review",
            public_id=enrollment.public_id,
        )

    if not settings.PAYSTACK_SECRET_KEY:
        messages.error(
            request,
            "Paystack is not configured. Add the test secret key to .env.",
        )
        return redirect(
            "payments:payment_review",
            public_id=enrollment.public_id,
        )

    reference = f"GA-{uuid.uuid4().hex}"

    payment = Payment.objects.create(
        pending_enrollment=enrollment,
        reference=reference,
        amount=enrollment.amount,
    )

    callback_url = request.build_absolute_uri(
        reverse("payments:verify_payment")
    )

    payload = {
        "email": enrollment.email,
        "amount": enrollment.amount * 100,
        "currency": "NGN",
        "reference": reference,
        "callback_url": callback_url,
        "metadata": {
            "pending_enrollment_id": enrollment.id,
            "student_type": enrollment.student_type,
            "course_name": enrollment.course_name,
        },
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=paystack_headers(),
            json=payload,
            timeout=20,
        )
        response_data = response.json()
    except requests.RequestException:
        messages.error(request, "Could not connect to Paystack.")
        return redirect(
            "payments:payment_review",
            public_id=enrollment.public_id,
        )
    except ValueError:
        messages.error(request, "Paystack returned an unexpected response.")
        return redirect(
            "payments:payment_review",
            public_id=enrollment.public_id,
        )

    if not response.ok or not response_data.get("status"):
        payment.status = Payment.Status.FAILED
        payment.provider_response = response_data
        payment.save(update_fields=["status", "provider_response"])

        messages.error(
            request,
            response_data.get("message", "Could not start payment."),
        )
        return redirect(
            "payments:payment_review",
            public_id=enrollment.public_id,
        )

    return redirect(response_data["data"]["authorization_url"])


def confirm_payment(payment, transaction_data):
    """
    Never trust the browser alone.
    Confirm Paystack status, reference, and amount on the server.
    """
    expected_amount = payment.amount * 100

    if (
        transaction_data.get("status") != "success"
        or transaction_data.get("reference") != payment.reference
        or int(transaction_data.get("amount", 0)) != expected_amount
    ):
        return False

    with transaction.atomic():
        payment = Payment.objects.select_for_update().select_related(
            "pending_enrollment"
        ).get(pk=payment.pk)

        enrollment = payment.pending_enrollment

        if payment.status == Payment.Status.PAID:
            return True

        payment.status = Payment.Status.PAID
        payment.provider_response = transaction_data
        payment.paid_at = timezone.now()
        payment.save(
            update_fields=["status", "provider_response", "paid_at"]
        )

        enrollment.payment_status = (
            PendingEnrollment.PaymentStatus.PAID
        )
        enrollment.paid_at = payment.paid_at
        enrollment.accepted_at = payment.paid_at
        enrollment.account_setup_token = uuid.uuid4()
        enrollment.setup_token_expires_at = timezone.now() + timedelta(hours=48)
        
        
        enrollment.registration_number = (
            f"GA-{timezone.localdate().year}-{enrollment.id:05d}"
        )
        enrollment.save(
            update_fields=[
                "payment_status",
                "paid_at",
                "accepted_at",
                "account_setup_token",
                "setup_token_expires_at",
                "registration_number",
            ]
        )

    return True


def send_account_setup_email(request, enrollment):
    setup_url = request.build_absolute_uri(
        reverse(
            "payments:account_setup",
            args=[enrollment.account_setup_token],
        )
    )

    send_mail(
        subject="Complete your Grey Academy account",
        message=(
            f"Hello {enrollment.first_name},\n\n"
            "Your payment has been confirmed.\n\n"
            "Use this link to create your Grey Academy account password:\n"
            f"{setup_url}\n\n"
            "This link expires in 48 hours."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[enrollment.email],
        fail_silently=False,
    )


@require_GET
def verify_payment_view(request):
    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "No payment reference was supplied.")
        return redirect("payments:get_started")

    payment = get_object_or_404(
        Payment.objects.select_related("pending_enrollment"),
        reference=reference,
    )

    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=paystack_headers(),
            timeout=20,
        )
        response_data = response.json()
    except requests.RequestException:
        messages.error(request, "Could not verify payment yet.")
        return redirect(
            "payments:payment_review",
            public_id=payment.pending_enrollment.public_id,
        )
    except ValueError:
        messages.error(request, "Paystack returned an unexpected response.")
        return redirect(
            "payments:payment_review",
            public_id=payment.pending_enrollment.public_id,
        )

    transaction_data = response_data.get("data", {})

    if response.ok and response_data.get("status") and confirm_payment(
        payment,
        transaction_data,
    ):
        enrollment = payment.pending_enrollment
        enrollment.refresh_from_db()

        if not enrollment.user:
            send_account_setup_email(request, enrollment)

        return render(
            request,
            "payments/payment_success.html",
            {"enrollment": enrollment},
        )

    payment.status = Payment.Status.FAILED
    payment.provider_response = response_data
    payment.save(update_fields=["status", "provider_response"])

    messages.error(
        request,
        "Payment was not confirmed, so registration has not been activated.",
    )
    return redirect(
        "payments:payment_review",
        public_id=payment.pending_enrollment.public_id,
    )


def account_setup_view(request, token):
    enrollment = get_object_or_404(
        PendingEnrollment,
        account_setup_token=token,
        payment_status=PendingEnrollment.PaymentStatus.PAID,
        user__isnull=True,
    )

    if (
        not enrollment.setup_token_expires_at
        or enrollment.setup_token_expires_at < timezone.now()
    ):
        messages.error(
            request,
            "This account-setup link has expired.",
        )
        return redirect("payments:get_started")

    if request.method == "POST":
        form = AccountSetupForm(request.POST)

        if form.is_valid():
            if User.objects.filter(
                email__iexact=enrollment.email
            ).exists():
                form.add_error(
                    None,
                    "An account already exists with this email.",
                )
            elif User.objects.filter(
                phone_number=enrollment.phone_number
            ).exists():
                form.add_error(
                    None,
                    "An account already exists with this phone number. "
                    "Please contact Grey Academy.",
                )
            else:
                user = User(
                    email=enrollment.email,
                    username=enrollment.email,
                    first_name=enrollment.first_name,
                    last_name=enrollment.last_name,
                    phone_number=enrollment.phone_number,
                    is_active=True,
                    is_verified=True,
                )
                user.set_password(form.cleaned_data["password1"])
                user.save()

                enrollment.user = user
                enrollment.account_completed_at = timezone.now()
                enrollment.account_setup_token = None
                enrollment.setup_token_expires_at = None
                enrollment.save(
                    update_fields=[
                        "user",
                        "account_completed_at",
                        "account_setup_token",
                        "setup_token_expires_at",
                    ]
                )

                login(request, user)
                return redirect("payments:registration_documents")
    else:
        form = AccountSetupForm()

    return render(
        request,
        "accounts/complete_account.html",
        {
            "form": form,
            "enrollment": enrollment,
        },
    )


@login_required
def registration_documents_view(request):
    enrollment = get_object_or_404(
        PendingEnrollment,
        user=request.user,
        payment_status=PendingEnrollment.PaymentStatus.PAID,
    )

    return render(
        request,
        "payments/registration_documents.html",
        {"enrollment": enrollment},
    )

@login_required
def biodata_form_view(request):
    enrollment = get_object_or_404(
        PendingEnrollment,
        user=request.user,
        payment_status=PendingEnrollment.PaymentStatus.PAID,
    )

    return render(
        request,
        "payments/biodata_form.html",
        {"enrollment": enrollment},
    )


@login_required
def siwes_acceptance_letter_view(request):
    enrollment = get_object_or_404(
        PendingEnrollment,
        user=request.user,
        student_type=PendingEnrollment.StudentType.SIWES,
        payment_status=PendingEnrollment.PaymentStatus.PAID,
    )

    return render(
        request,
        "payments/siwes_acceptance_letter.html",
        {"enrollment": enrollment},
    )


@login_required
def download_siwes_acceptance_letter_view(request):
    enrollment = get_object_or_404(
        PendingEnrollment,
        user=request.user,
        student_type=PendingEnrollment.StudentType.SIWES,
        payment_status=PendingEnrollment.PaymentStatus.PAID,
    )

    html = render_to_string(
        "payments/siwes_acceptance_letter_pdf.html",
        {"enrollment": enrollment},
    )

    filename = (
        f"grey-academy-siwes-acceptance-"
        f"{enrollment.first_name}-{enrollment.last_name}.pdf"
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    pdf_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=pdf_link_callback,
        resource_policy=PDF_RESOURCE_POLICY,
    )

    if pdf_status.err:
        return HttpResponse(
            "We could not generate the acceptance letter PDF.",
            status=500,
        )

    return response

@csrf_exempt
@require_POST
def paystack_webhook_view(request):
    """
    Add this URL to Paystack only after deploying the project publicly.
    Paystack cannot reach localhost.
    """
    signature = request.headers.get("x-paystack-signature", "")

    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        request.body,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return HttpResponseBadRequest("Invalid Paystack signature.")

    try:
        event = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return HttpResponseBadRequest("Invalid JSON.")

    if event.get("event") != "charge.success":
        return HttpResponse(status=200)

    transaction_data = event.get("data", {})
    reference = transaction_data.get("reference")

    payment = Payment.objects.filter(reference=reference).first()

    if payment:
        confirm_payment(payment, transaction_data)

    return HttpResponse(status=200)