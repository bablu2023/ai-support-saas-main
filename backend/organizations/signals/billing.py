from django.db.models.signals import post_migrate
from django.dispatch import receiver

from billing.models import Plan
from organizations.models import Organization

@receiver(post_migrate)
def create_default_plan(sender, **kwargs):
    free_plan, _ = Plan.objects.get_or_create(
        name="Free",
        defaults={
            "monthly_token_limit": 10000,
            "price": 0,
        },
    )

    Organization.objects.filter(plan__isnull=True).update(
        plan=free_plan
    )
