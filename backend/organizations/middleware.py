from django.http import JsonResponse
from organizations.models import Organization, OrganizationMember

class OrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.org_member = None

        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)

        org_id = request.headers.get("X-Organization-ID")

        # If no org header, continue (public / auth endpoints)
        if not org_id:
            return self.get_response(request)

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return JsonResponse(
                {"detail": "Invalid organization"},
                status=400,
            )

        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True,
            )
        except OrganizationMember.DoesNotExist:
            return JsonResponse(
                {"detail": "Not a member of this organization"},
                status=403,
            )

        request.organization = organization
        request.org_member = membership

        return self.get_response(request)
