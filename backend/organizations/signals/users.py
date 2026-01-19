from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from organizations.models import Organization, OrganizationMember
from organizations.constants import ORG_OWNER

User = get_user_model()

@receiver(post_save, sender=User)
def create_org_for_new_user(sender, instance, created, **kwargs):
    if not created:
        return

    # prevent duplicates (very important)
    if OrganizationMember.objects.filter(user=instance).exists():
        return

    organization = Organization.objects.create(
        name=f"{instance.username}'s Organization"
    )

    OrganizationMember.objects.create(
        user=instance,
        organization=organization,
        role=ORG_OWNER,
        is_active=True,
    )
