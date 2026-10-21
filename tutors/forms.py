from django.contrib.auth import get_user_model
from django import forms

from .models import TUTOR_FIELDS, TutorProfile

User = get_user_model()
MAX_TUTOR_PHOTO_SIZE = 2 * 1024 * 1024

class TutorSignupForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    field = forms.ChoiceField(choices=TUTOR_FIELDS, label="What do you tutor?")
    bio = forms.CharField(widget=forms.Textarea, required=False)
    password1 = forms.CharField(label="Password", min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account already exists with this email.")

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()

        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("An account already exists with this phone number.")

        return phone

    def clean(self):
        cleaned = super().clean()

        if (
            cleaned.get("password1")
            and cleaned.get("password2")
            and cleaned["password1"] != cleaned["password2"]
        ):
            self.add_error("password2", "Passwords do not match.")

        return cleaned


class LessonForm(forms.Form):
    title = forms.CharField(max_length=200)
    video_url = forms.URLField(label="Video link")
    message = forms.CharField(widget=forms.Textarea, required=False)
