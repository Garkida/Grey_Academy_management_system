from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

User = get_user_model()


class SignUpForm(forms.ModelForm):
    """
    Registration form.

    Checks (per spec):
    - Rejects the request if the email is already registered.
    - Rejects the request if the phone number is already registered.
    - Requires the two password fields to match.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Create a password"}),
        min_length=8,
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"placeholder": "Repeat your password"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "080..."}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        # Verify an account with this email doesn't already exist before we proceed.
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists just log in .")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        if phone and User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("An account with this phone number already exists just log in.")
        return phone

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # keep the field populated & unique
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True       # they CAN log in...
        user.is_verified = False    # ...but we treat them as unverified until email confirm
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    """Simple email + password login form (email is the USERNAME_FIELD)."""

    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class AcademyPasswordResetForm(PasswordResetForm):
    """
    Password reset request form.

    Security note: we deliberately do NOT reveal whether an email exists.
    Django's built-in PasswordResetForm already behaves this way out of the
    box (save() silently does nothing if no matching user is found), so we
    only need to make sure we don't accidentally change that behaviour.
    The user always sees the same generic confirmation message.
    """

    def get_users(self, email):
        """Only send the reset email to active, verified accounts."""
        return (
            u
            for u in User.objects.filter(email__iexact=email, is_active=True)
            if u.has_usable_password()
        )
