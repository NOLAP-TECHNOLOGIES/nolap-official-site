from django.contrib import admin

from .models import Choice, Form, Question, Step


class StepInline(admin.TabularInline):
    model = Step
    extra = 1
    ordering = ["order"]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    ordering = ["order"]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    ordering = ["order"]


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("title", "organiser", "form_type", "status", "created_at")
    list_filter = ("status", "form_type")
    search_fields = ("title", "organiser__organisation_name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [StepInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ("__str__", "form", "order")
    list_filter = ("form",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("label", "step", "field_type", "required", "order")
    list_filter = ("field_type", "required")
    search_fields = ("label",)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("label", "question", "order")
