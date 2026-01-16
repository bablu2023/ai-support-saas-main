from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from organizations.permissions import can_edit_knowledge


@api_view(["POST"])
def upload_knowledge(request):
    org = request.organization  # however you attach it
    user = request.user

    if not can_edit_knowledge(user, org):
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    # upload logic here

