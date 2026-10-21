from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse

from .forms import SignUpForm, EmailLoginForm
from .models import EmailVerificationToken

User = get_user_model()


def _send_verification_email(request, user):
    """
    Create a fresh 1-minute token for this user and email the link.
    Any older, unused tokens for the same user are deleted first so a
    user can never verify with a stale link.
    """
    EmailVerificationToken.objects.filter(user=user).delete()
    token_obj = EmailVerificationToken.objects.create(
        user=user, token=EmailVerificationToken.generate_token()
    )
    verify_url = request.build_absolute_uri(
        reverse("accounts:verify_email", args=[token_obj.token])
    )
    
     # DEV CONVENIENCE ONLY: prints a clean, unwrapped link for local testing
    if settings.DEBUG:
        print(f"\n[DEV] Verification link for {user.email}:\n{verify_url}\n") 
    
    send_mail(
        subject="Confirm your Grey Academy account",
        message=(
            f"Hi {user.first_name or user.email},\n\n"
            f"Click the link below to verify your email address. "
            f"This link expires in 1 minute:\n\n{verify_url}\n\n"
            f"If you didn't create this account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return token_obj
  

def signup_view(request):
    return redirect("payments:get_started")
    #     return redirect("core:dashboard")

    # if request.method == "POST":
    #     form = SignUpForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         token_obj = _send_verification_email(request, user)
    #         request.session["pending_verification_user_id"] = user.id
    #         return redirect("accounts:verify_email_sent")
    # else:
    #     form = SignUpForm()

    # return render(request, "accounts/signup.html", {"form": form})


def verify_email_sent_view(request):
    """
    The 'check your inbox' page. Shows the live 1-minute countdown and
    a resend button (enabled once the countdown reaches zero).
    """
    user_id = request.session.get("pending_verification_user_id")
    if not user_id:
        return redirect("accounts:signup")
    
    user = get_object_or_404(User, id=user_id)
    token_obj = EmailVerificationToken.objects.filter(user=user).order_by("-created_at").first()
    seconds_remaining = token_obj.seconds_remaining if token_obj else 0

    return render(
        request,
        "accounts/verify_email_sent.html",
        {"user_email": user.email, "seconds_remaining": seconds_remaining},)
    
    
def verification_status_view(request):
        """Tiny JSON endpoint the countdown page polls to detect verification."""
        
        user_id = request.session.get("pending_verification_user_id")
        if not user_id:
            return JsonResponse({"verified": False})
        is_verified = User.objects.filter(id=user_id, is_verified=True).exists()
        return JsonResponse({"verified": is_verified})
        


def resend_verification_view(request):
    """Issue a brand-new token + email, restarting the 1-minute countdown."""
    user_id = request.session.get("pending_verification_user_id")
    if not user_id:
        return redirect("accounts:signup")

    user = get_object_or_404(User, id=user_id)
    if user.is_verified:
        messages.info(request, "This account is already verified — you can log in.")
        return redirect("accounts:login")

    _send_verification_email(request, user)
    messages.success(request, "A new verification link has been sent to your email.")
    return redirect("accounts:verify_email_sent")


def verify_email_view(request, token):
    """
    The link the user clicks from their email.
    Rejects the token if it doesn't exist or has expired (>1 minute old).
    """
    token_obj = EmailVerificationToken.objects.filter(token=token).first()

    if token_obj is None:
        messages.error(request, "This verification link is invalid.")
        return redirect("accounts:signup")

    if token_obj.is_expired:
        messages.error(request, "This verification link has expired. Please request a new one.")
        return redirect("accounts:verify_email_sent")

    user = token_obj.user
    user.is_verified = True
    user.save(update_fields=["is_verified"])
    token_obj.delete()

    messages.success(request, "Your email has been verified — you can now log in.")
    return redirect("accounts:login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is None:
                form.add_error(None, "Incorrect email or password.")
            elif not user.is_verified:
                messages.warning(
                    request, "Please verify your email before logging in."
                )
                request.session["pending_verification_user_id"] = user.id
                return redirect("accounts:verify_email_sent")
            else:
                login(request, user)
                return redirect("core:dashboard")
    else:
        form = EmailLoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out.")
    return redirect("core:home")
