from django.conf import settings
from django.db import models
import uuid
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=255)

    plan = models.ForeignKey(
        "billing.Plan",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organizations",
    )

    monthly_tokens_used = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ("owner", "Owner"),
            ("admin", "Admin"),
            ("member", "Member"),
        ],
        default="member",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"
    



class OrganizationInvite(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=[
            ("admin", "Admin"),
            ("member", "Member"),
        ],
        default="member",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.accepted_at is None

    def mark_accepted(self):
        self.accepted_at = timezone.now()
        self.save(update_fields=["accepted_at"])

