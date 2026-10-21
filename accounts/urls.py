from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import AcademyPasswordResetForm

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("verify-email/sent/", views.verify_email_sent_view, name="verify_email_sent"),
    path("verify-email/resend/", views.resend_verification_view, name="resend_verification"),
    path("verify-email/<str:token>/", views.verify_email_view, name="verify_email"),
    path("verify-email/status/", views.verification_status_view, name="verification_status"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    
    # --- Password reset flow (Django's built-in class-based views) ---
    # Step 1: user enters their email.
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            form_class=AcademyPasswordResetForm,
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    # Step 2: generic "check your inbox" page (shown whether or not the
    # email actually existed — this is what keeps the flow from leaking
    # which emails are registered).
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # Step 3: the link from the email — set a new password.
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    # Step 4: confirmation.
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

from django.contrib.auth import views as auth_views

urlpatterns += [
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/dashboard/",
        ),
        name="password_change",
    ),
]