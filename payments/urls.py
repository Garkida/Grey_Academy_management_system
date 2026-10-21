from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("get-started/", views.get_started_view, name="get_started"),
    path(
        "register/<str:student_type>/",
        views.registration_view,
        name="registration",
    ),
    path(
        "review/<uuid:public_id>/",
        views.payment_review_view,
        name="payment_review",
    ),
    path(
        "start/<uuid:public_id>/",
        views.start_payment_view,
        name="start_payment",
    ),
    path("verify/", views.verify_payment_view, name="verify_payment"),
    path(
        "setup/<uuid:token>/",
        views.account_setup_view,
        name="account_setup",
    ),
    path(
        "documents/",
        views.registration_documents_view,
        name="registration_documents",
    ),
    path(
        "biodata/",
        views.biodata_form_view,
        name="biodata_form",
    ),
    path(
        "acceptance-letter/",
        views.siwes_acceptance_letter_view,
        name="siwes_acceptance_letter",
    ),

    path(
    "acceptance-letter/download/",
    views.download_siwes_acceptance_letter_view,
    name="download_siwes_acceptance_letter",
),
    path(
        "webhook/",
        views.paystack_webhook_view,
        name="paystack_webhook",
    ),
]