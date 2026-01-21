from django.db import models
from django.conf import settings
from organizations.models import Organization
from django.utils.timezone import now

class AgentRun(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="agent_runs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_runs",
    )

    agent_name = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queued",
    )

    input_text = models.TextField()
    output = models.JSONField(null=True, blank=True)
    actions = models.JSONField(null=True, blank=True)

    tokens_used = models.PositiveIntegerField(default=0)

    error = models.TextField(null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.agent_name} ({self.status})"
    



    


class AgentApproval(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    run = models.ForeignKey(
        AgentRun,
        on_delete=models.CASCADE,
        related_name="approvals",
    )

    tool_name = models.CharField(max_length=100)

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_approvals_requested",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="agent_approvals_decided",
    )

    decided_at = models.DateTimeField(null=True, blank=True)

    reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def approve(self, user):
        self.status = "approved"
        self.decided_by = user
        self.decided_at = now()
        self.save()

    def reject(self, user, reason=None):
        self.status = "rejected"
        self.decided_by = user
        self.decided_at = now()
        self.reason = reason
        self.save()

    def __str__(self):
        return f"Approval for {self.tool_name} ({self.status})"

