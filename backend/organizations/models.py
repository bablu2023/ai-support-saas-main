from django.conf import settings
from django.db import models
import secrets   # 👈 ADD THIS


class Organization(models.Model):
    name = models.CharField(max_length=255)
    plan = models.ForeignKey(
        "billing.Plan",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organizations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    api_key = models.CharField(          # 👈 ADD THIS BLOCK
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )

    def save(self, *args, **kwargs):      # 👈 ADD THIS METHOD
        if not self.api_key:
            self.api_key = "org_" + secrets.token_hex(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
