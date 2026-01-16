from django.contrib import admin
from .models import Plan
from .models import Plan, TokenUsage





@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_token_limit", "price")


@admin.register(TokenUsage)
class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ("organization", "total_tokens", "created_at")
    list_filter = ("organization",)









