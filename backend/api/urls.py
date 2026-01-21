from django.urls import path
from .views import (
    chat_api,
    widget_snippet,
    upload_text_knowledge,
    chat_logs,
    health,
    invite_user,
    accept_invite,
    agent_task,
    agent_workflow,   # 👈 ADD THIS LINE
    approve_agent_tool,
    reject_agent_tool,
)

urlpatterns = [
    path("chat/", chat_api),
    path("chat/logs/", chat_logs),
    path("widget/snippet/", widget_snippet),
    path("knowledge/text/", upload_text_knowledge),
    path("health/", health, name="health"),
    path("agent/task/", agent_task),
    path("agent/workflow/", agent_workflow),
    path(
    "agent/approval/<int:approval_id>/approve/",
    approve_agent_tool,
    ),
    path(
    "agent/approval/<int:approval_id>/reject/",
    reject_agent_tool,
    ),
    path("agent/approvals/pending/", pending_approvals),



]
















