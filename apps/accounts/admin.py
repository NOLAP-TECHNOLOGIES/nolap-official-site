from django.contrib import admin

from .models import Organiser


@admin.register(Organiser)
class OrganiserAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "phone", "created_at")
    search_fields = ("user__email", "organisation_name", "phone")
    readonly_fields = ("created_at",)
