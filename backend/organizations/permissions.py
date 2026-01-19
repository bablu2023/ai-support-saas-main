from .models import OrganizationMember
from organizations.models import OrganizationMember


def has_role(user, organization, roles):
    return OrganizationMember.objects.filter(
        user=user,
        organization=organization,
        role__in=roles
    ).exists()


def is_owner(user, organization):
    return has_role(user, organization, ["owner"])


def is_admin(user, organization):
    return has_role(user, organization, ["owner", "admin"])


def can_edit_knowledge(user, organization):
    return has_role(user, organization, ["owner", "admin", "editor"])


def can_view_only(user, organization):
    return has_role(user, organization, ["viewer"])





def user_has_role(user, organization, allowed_roles):
    if not user or not user.is_authenticated:
        return False

    return OrganizationMember.objects.filter(
        user=user,
        organization=organization,
        role__in=allowed_roles,
        is_active=True,
    ).exists()

