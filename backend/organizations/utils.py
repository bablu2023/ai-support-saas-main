def generate_widget_snippet(org):
    return f"""<script
  src="http://127.0.0.1:8000/widget/widget.js"
  data-org-key="{org.api_key}">
</script>"""

from .models import OrganizationMember


def user_has_role(user, organization, roles):
    if not user.is_authenticated:
        return False

    return OrganizationMember.objects.filter(
        user=user,
        organization=organization,
        role__in=roles
    ).exists()
