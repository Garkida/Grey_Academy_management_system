from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import EmailVerificationToken, User
from django import forms


class UserAddForm(UserCreationForm):
    """Add-user form that also collects phone number and sets username = email."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "phone_number", "is_verified")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin view for our custom User model (email-based login)."""

    add_form = UserAddForm

    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "phone_number", "is_verified", "is_staff", "is_active"]
    list_filter = ["is_verified", "is_staff", "is_active", "track"]
    search_fields = ["email", "first_name", "last_name", "phone_number"]

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number", "track")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "is_verified",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "expires_at", "is_expired"]
    readonly_fields = ["token", "created_at"]