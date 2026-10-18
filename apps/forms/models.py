from django.db import models
from django.utils.text import slugify

from apps.accounts.models import Organiser


class Form(models.Model):
    FORM_TYPES = [
        ("blank", "Blank"),
        ("survey", "Survey"),
        ("registration", "Registration"),
        ("quiz", "Quiz"),
        ("event", "Event"),
        ("scholarship", "Scholarship"),
        ("job", "Job Application"),
        ("admissions", "Admissions"),
        ("membership", "Membership"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("live", "Live"),
        ("closed", "Closed"),
    ]

    organiser = models.ForeignKey(
        Organiser, on_delete=models.CASCADE, related_name="forms"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=220, unique=True)
    form_type = models.CharField(max_length=20, choices=FORM_TYPES, default="blank")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    collect_phone = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "form"
            slug = base
            n = 1
            while Form.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def response_count(self):
        return self.responses.count() if hasattr(self, "responses") else 0


class Step(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="steps")
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Step {self.order + 1}"


class Question(models.Model):
    GHANA_FIELD_TYPES = [
        ("phone_gh", "Phone number (Ghana)"),
        ("ghana_card", "Ghana Card"),
        ("region", "Region"),
        ("digital_address", "Digital address"),
    ]

    STANDARD_FIELD_TYPES = [
        ("short_text", "Short text"),
        ("long_text", "Long text"),
        ("single_choice", "Single choice"),
        ("multiple_choice", "Multiple choice"),
        ("dropdown", "Dropdown"),
        ("date", "Date"),
        ("email", "Email"),
        ("contact_preference", "Contact preference"),
        ("file_upload", "File upload"),
        ("rating", "Rating"),
        ("number", "Number"),
    ]

    FIELD_TYPES = GHANA_FIELD_TYPES + STANDARD_FIELD_TYPES

    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name="questions")
    label = models.CharField(max_length=500)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)
    help_text = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label

    @property
    def has_choices(self):
        return self.field_type in ("single_choice", "multiple_choice", "dropdown")

    @property
    def is_ghana_field(self):
        return self.field_type in dict(self.GHANA_FIELD_TYPES)


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    label = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label
