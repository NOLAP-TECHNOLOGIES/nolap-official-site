from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from apps.accounts.models import Organiser

User = get_user_model()


def make_user(email="test@example.com", password="pass", **kwargs):
    return User.objects.create_user(
        username=email, email=email, password=password, **kwargs
    )


class OrganiserModelTest(TestCase):
    def test_str_uses_organisation_name(self):
        user = make_user(email="a@b.com")
        org = Organiser.objects.create(user=user, organisation_name="Acme")
        self.assertEqual(str(org), "Acme")

    def test_str_falls_back_to_full_name(self):
        user = make_user(email="a@b.com", first_name="Kofi", last_name="Mensah")
        org = Organiser.objects.create(user=user)
        self.assertEqual(str(org), "Kofi Mensah")

    def test_str_falls_back_to_email(self):
        user = make_user(email="a@b.com")
        org = Organiser.objects.create(user=user)
        self.assertEqual(str(org), "a@b.com")


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login", resp.url)

    def test_logged_in_user_sees_dashboard(self):
        self.client.login(username="test@example.com", password="pass")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Your Forms")

    def test_dashboard_shows_empty_state(self):
        self.client.login(username="test@example.com", password="pass")
        resp = self.client.get("/dashboard/")
        self.assertContains(resp, "No forms yet")


class SignalTest(TestCase):
    def test_organiser_created_on_signup_signal(self):
        from allauth.account.signals import user_signed_up

        user = make_user(email="new@example.com")
        request = RequestFactory().get("/")
        request.session = {}
        user_signed_up.send(sender=user.__class__, request=request, user=user)
        self.assertTrue(Organiser.objects.filter(user=user).exists())
