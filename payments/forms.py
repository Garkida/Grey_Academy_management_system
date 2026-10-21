from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model

from .catalog import ACADEMY_COURSES, SIWES_COURSES
from .models import PendingEnrollment

User = get_user_model()

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_PHOTO_SIZE = 2 * 1024 * 1024


class BaseRegistrationForm(forms.ModelForm):
    passport_photo = forms.ImageField(
        help_text="Upload a JPG, JPEG, or PNG image under 2 MB."
    )

    class Meta:
        model = PendingEnrollment
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "course_key",
            "passport_photo",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account already exists with this email. Please log in."
            )

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()

        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError(
                "An account already exists with this phone number."
            )

        return phone

    def clean_passport_photo(self):
        photo = self.cleaned_data["passport_photo"]

        if photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError("Passport photograph must be 2 MB or smaller.")

        if photo.image.width < 300 or photo.image.height < 300:
            raise forms.ValidationError(
                "Passport photograph must be at least 300 by 300 pixels."
            )

        return photo


class GreyAcademyRegistrationForm(BaseRegistrationForm):
    course_key = forms.ChoiceField(
        choices=ACADEMY_COURSES.items(),
        label="Choose a course",
    )


class SIWESRegistrationForm(BaseRegistrationForm):
    course_key = forms.ChoiceField(
        choices=SIWES_COURSES.items(),
        label="SIWES area",
    )

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + [
            "other_course_name",
            "institution_name",
            "course_of_study",
            "matric_number",
            "school_application_letter",
        ]

    def clean_school_application_letter(self):
        letter = self.cleaned_data["school_application_letter"]
        extension = Path(letter.name).suffix.lower()

        if extension not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise forms.ValidationError(
                "Application letter must be PDF, JPG, JPEG, or PNG."
            )

        if letter.size > MAX_FILE_SIZE:
            raise forms.ValidationError("Application letter must be 5 MB or smaller.")

        return letter

    def clean(self):
        cleaned = super().clean()

        course_key = cleaned.get("course_key")
        other_course_name = cleaned.get("other_course_name", "").strip()

        if course_key == "other" and not other_course_name:
            self.add_error(
                "other_course_name",
                "State your SIWES area when you select Other.",
            )

        if course_key != "other":
            cleaned["other_course_name"] = ""

        return cleaned


class AccountSetupForm(forms.Form):
    password1 = forms.CharField(
        label="Create password",
        min_length=8,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned = super().clean()

        if (
            cleaned.get("password1")
            and cleaned.get("password2")
            and cleaned["password1"] != cleaned["password2"]
        ):
            self.add_error("password2", "Passwords do not match.")

        return cleaned
