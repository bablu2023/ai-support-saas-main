from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify

from .models import Organization, OrganizationMember


@api_view(["POST"])
def create_organization(request):
    user = request.user   # logged-in admin
    name = request.data.get("name")

    if not name:
        return Response({"error": "Organization name required"}, status=400)

    org = Organization.objects.create(
        name=name,
        slug=slugify(name),
        api_key=Organization.generate_api_key()  # or your method
    )

    # 🔑 STEP 5 — OWNER ASSIGNMENT (PUT HERE)
    OrganizationMember.objects.create(
        user=user,
        organization=org,
        role="owner"
    )

    return Response({
        "message": "Organization created",
        "organization": org.slug
    }, status=201)

