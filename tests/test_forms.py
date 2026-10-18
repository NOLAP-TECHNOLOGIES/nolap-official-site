from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import Organiser
from apps.forms.models import Choice, Form, Question, Step
from apps.forms.validators import (
    detect_carrier,
    validate_digital_address,
    validate_ghana_card,
    validate_ghana_phone,
)

User = get_user_model()


def make_user(email="test@example.com", password="pass", **kwargs):
    return User.objects.create_user(
        username=email, email=email, password=password, **kwargs
    )


def make_form(organiser, **kwargs):
    defaults = {"title": "Test Form", "organiser": organiser}
    defaults.update(kwargs)
    return Form.objects.create(**defaults)


class FormModelTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.organiser = Organiser.objects.create(
            user=self.user, organisation_name="Test Org"
        )

    def test_str(self):
        form = make_form(self.organiser, title="My Survey")
        self.assertEqual(str(form), "My Survey")

    def test_auto_slug(self):
        form = make_form(self.organiser, title="My Survey")
        self.assertEqual(form.slug, "my-survey")

    def test_slug_uniqueness(self):
        make_form(self.organiser, title="My Survey")
        form2 = make_form(self.organiser, title="My Survey")
        self.assertEqual(form2.slug, "my-survey-1")

    def test_default_status_is_draft(self):
        form = make_form(self.organiser)
        self.assertEqual(form.status, "draft")

    def test_default_form_type_is_blank(self):
        form = make_form(self.organiser)
        self.assertEqual(form.form_type, "blank")

    def test_ordering_newest_first(self):
        f1 = make_form(self.organiser, title="First")
        f2 = make_form(self.organiser, title="Second")
        forms = list(Form.objects.all())
        self.assertEqual(forms[0], f2)
        self.assertEqual(forms[1], f1)


class StepModelTest(TestCase):
    def setUp(self):
        user = make_user()
        organiser = Organiser.objects.create(user=user)
        self.form = make_form(organiser)

    def test_str_with_title(self):
        step = Step.objects.create(form=self.form, title="Personal Info", order=0)
        self.assertEqual(str(step), "Personal Info")

    def test_str_without_title(self):
        step = Step.objects.create(form=self.form, order=0)
        self.assertEqual(str(step), "Step 1")

    def test_ordering(self):
        s2 = Step.objects.create(form=self.form, title="B", order=1)
        s1 = Step.objects.create(form=self.form, title="A", order=0)
        steps = list(self.form.steps.all())
        self.assertEqual(steps, [s1, s2])


class QuestionModelTest(TestCase):
    def setUp(self):
        user = make_user()
        organiser = Organiser.objects.create(user=user)
        form = make_form(organiser)
        self.step = Step.objects.create(form=form, order=0)

    def test_str(self):
        q = Question.objects.create(
            step=self.step, label="What is your name?", field_type="short_text"
        )
        self.assertEqual(str(q), "What is your name?")

    def test_has_choices_for_single_choice(self):
        q = Question.objects.create(
            step=self.step, label="Pick one", field_type="single_choice"
        )
        self.assertTrue(q.has_choices)

    def test_has_choices_false_for_text(self):
        q = Question.objects.create(
            step=self.step, label="Name", field_type="short_text"
        )
        self.assertFalse(q.has_choices)

    def test_is_ghana_field(self):
        q = Question.objects.create(
            step=self.step, label="Phone", field_type="phone_gh"
        )
        self.assertTrue(q.is_ghana_field)

    def test_is_not_ghana_field(self):
        q = Question.objects.create(
            step=self.step, label="Email", field_type="email"
        )
        self.assertFalse(q.is_ghana_field)

    def test_default_required(self):
        q = Question.objects.create(
            step=self.step, label="Name", field_type="short_text"
        )
        self.assertTrue(q.required)


class ChoiceModelTest(TestCase):
    def setUp(self):
        user = make_user()
        organiser = Organiser.objects.create(user=user)
        form = make_form(organiser)
        step = Step.objects.create(form=form, order=0)
        self.question = Question.objects.create(
            step=step, label="Pick one", field_type="single_choice"
        )

    def test_str(self):
        c = Choice.objects.create(question=self.question, label="Option A")
        self.assertEqual(str(c), "Option A")

    def test_ordering(self):
        c2 = Choice.objects.create(question=self.question, label="B", order=1)
        c1 = Choice.objects.create(question=self.question, label="A", order=0)
        choices = list(self.question.choices.all())
        self.assertEqual(choices, [c1, c2])


class GhanaPhoneValidatorTest(TestCase):
    def test_valid_local_format(self):
        validate_ghana_phone("024 123 4567")

    def test_valid_international_format(self):
        validate_ghana_phone("+233 24 123 4567")

    def test_valid_no_spaces(self):
        validate_ghana_phone("0241234567")

    def test_invalid_prefix(self):
        with self.assertRaises(ValidationError):
            validate_ghana_phone("0181234567")

    def test_too_short(self):
        with self.assertRaises(ValidationError):
            validate_ghana_phone("024123456")

    def test_too_long(self):
        with self.assertRaises(ValidationError):
            validate_ghana_phone("02412345678")


class GhanaCardValidatorTest(TestCase):
    def test_valid(self):
        validate_ghana_card("GHA-123456789-0")

    def test_valid_lowercase(self):
        validate_ghana_card("gha-123456789-0")

    def test_invalid_format(self):
        with self.assertRaises(ValidationError):
            validate_ghana_card("123456789")

    def test_wrong_prefix(self):
        with self.assertRaises(ValidationError):
            validate_ghana_card("ABC-123456789-0")


class DigitalAddressValidatorTest(TestCase):
    def test_valid(self):
        validate_digital_address("AK-039-5028")

    def test_valid_lowercase(self):
        validate_digital_address("ak-039-5028")

    def test_valid_four_digit_middle(self):
        validate_digital_address("GA-1234-5678")

    def test_invalid(self):
        with self.assertRaises(ValidationError):
            validate_digital_address("12345")


class CarrierDetectionTest(TestCase):
    def test_mtn(self):
        self.assertEqual(detect_carrier("024 123 4567"), "MTN")

    def test_telecel(self):
        self.assertEqual(detect_carrier("020 123 4567"), "Telecel")

    def test_airteltigo(self):
        self.assertEqual(detect_carrier("026 123 4567"), "AirtelTigo")

    def test_international_format(self):
        self.assertEqual(detect_carrier("+233 24 123 4567"), "MTN")

    def test_unknown_prefix(self):
        self.assertIsNone(detect_carrier("018 123 4567"))
