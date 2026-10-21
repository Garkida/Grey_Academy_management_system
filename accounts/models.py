import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom manager so we can create users with EMAIL as the login field
    instead of Django's default 'username' field.
    """

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model.

    - Login happens with EMAIL, not username (username is kept but unused
      by the login form; Django still likes having it internally).
    - Adds phone_number, since the academy signup form asks for it.
    - Adds is_verified so we can gate access until the user confirms
      their email address.
    """

    email = models.EmailField("email address", unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Set to True once the user confirms their email address.",
    )
    track = models.CharField(
        max_length=30,
        blank=True,
        help_text="Which Grey Academy course track the student picked, if any.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # 'email' is already required by USERNAME_FIELD

    objects = UserManager()

    def __str__(self):
        return self.email


def default_expiry():
    """A verification token is only valid for 1 minute after creation."""
    return timezone.now() + timedelta(minutes=1)


class EmailVerificationToken(models.Model):
    """
    One-time token emailed to the user after signup.
    Expires 1 minute after it is created (per project spec).
    A fresh token can be generated any time via the 'resend' view,
    which simply deletes the old one and creates a new one.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    def __str__(self):
        return f"Verification token for {self.user.email}"

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(16)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def seconds_remaining(self):
        remaining = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))
