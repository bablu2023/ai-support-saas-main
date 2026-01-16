from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "plan", "created_at")
    list_filter = ("plan",)
    search_fields = ("name",)
