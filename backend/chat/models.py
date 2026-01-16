from django.db import models
from organizations.models import Organization


class ChatSession(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user_identifier = models.CharField(
        max_length=255,
        help_text="Anonymous user id or customer id",
    )
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} ({self.organization.name})"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} @ {self.created_at}"

