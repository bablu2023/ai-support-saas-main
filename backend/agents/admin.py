from django.contrib import admin
from agents.models import AgentRun


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "agent_name",
        "organization",
        "user",
        "status",
        "tokens_used",
        "started_at",
    )
    list_filter = ("status", "agent_name")
    search_fields = ("agent_name", "user__username")
