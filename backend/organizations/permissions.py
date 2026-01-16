from .models import OrganizationMember


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
