from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationNavigationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="student@example.com",
            password="safe-password-123",
            is_verified=True,
        )

    def test_home_shows_login_and_signup_for_visitors(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, 'href="/accounts/login/"')
        self.assertContains(response, 'href="/accounts/signup/"')
        self.assertNotContains(response, ">Log out<")

    def test_home_shows_dashboard_and_logout_for_signed_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, 'href="/dashboard/"')
        self.assertContains(response, ">Log out<")
        self.assertNotContains(response, ">Create account<")

    def test_logout_returns_user_to_home_and_clears_session(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("core:home"))
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, ">Log in<")
        self.assertNotContains(response, ">Log out<")
