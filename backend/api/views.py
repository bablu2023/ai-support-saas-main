from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from organizations.models import Organization
from organizations.utils import generate_widget_snippet

from billing.enforcement import enforce_token_limit, UsageLimitExceeded


from chat.services.retrieval import rag_chat
from chat.models import ChatSession, ChatMessage

from knowledge.services.ingestion import ingest_plain_text



from django.http import JsonResponse

from organizations.permissions import user_has_role
from organizations.constants import ORG_OWNER, ORG_ADMIN


from agents.executor import run_agent
from agents.task_agent import TaskAgent


from organizations.models import OrganizationInvite



from organizations.models import OrganizationMember

from agents.workflow_agent import WorkflowAgent

# =========================
# CHAT API (ENFORCED)
# =========================
@api_view(["POST"])
def chat_api(request):
    api_key = request.data.get("api_key")
    user_id = request.data.get("user_id")
    question = request.data.get("question")

    if not api_key or not user_id or not question:
        return Response(
            {"error": "api_key, user_id, and question are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        organization = Organization.objects.get(api_key=api_key)
    except Organization.DoesNotExist:
        return Response(
            {"error": "Invalid API key"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # 🔐 ENFORCEMENT (BEFORE AI CALL)
    estimated_tokens = len(question) // 4  # simple, safe estimate

    try:
        enforce_chat_limit(
            organization=organization,
            tokens_used=estimated_tokens,
        )
    except UsageLimitExceeded as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # 🤖 AI CALL (SAFE NOW)
    answer = rag_chat(
        organization=organization,
        user_id=user_id,
        query=question,
    )

    return Response(
        {
            "answer": answer,
            "organization": organization.name,
            "user_id": user_id,
        },
        status=status.HTTP_200_OK,
    )


# =========================
# WIDGET EMBED
# =========================
@api_view(["GET"])
def widget_snippet(request):
    api_key = request.query_params.get("api_key", "").strip()

    if not api_key:
        return Response(
            {"error": "api_key required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        organization = Organization.objects.get(api_key=api_key)
    except Organization.DoesNotExist:
        return Response(
            {"error": "Invalid API key"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response(
        {"widget_snippet": generate_widget_snippet(organization)},
        status=status.HTTP_200_OK,
    )


# =========================
# KNOWLEDGE INGESTION
# =========================
@api_view(["POST"])
def upload_text_knowledge(request):
    api_key = request.data.get("api_key")
    title = request.data.get("title")
    text = request.data.get("text")

    if not api_key or not title or not text:
        return Response(
            {"error": "api_key, title, and text are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        organization = Organization.objects.get(api_key=api_key)
    except Organization.DoesNotExist:
        return Response(
            {"error": "Invalid API key"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    ingest_plain_text(
        organization=organization,
        title=title,
        text=text,
    )

    return Response(
        {"status": "uploaded"},
        status=status.HTTP_200_OK,
    )


# =========================
# CHAT LOGS (ADMIN / USER)
# =========================
@api_view(["GET"])
def chat_logs(request):
    api_key = request.query_params.get("api_key", "").strip()

    if not api_key:
        return Response(
            {"error": "api_key required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        organization = Organization.objects.get(api_key=api_key)
    except Organization.DoesNotExist:
        return Response(
            {"error": "Invalid API key"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    sessions = ChatSession.objects.filter(
        organization=organization
    ).order_by("-id")

    response_data = []

    for session in sessions:
        messages = ChatMessage.objects.filter(
            session=session
        ).order_by("created_at")

        response_data.append(
            {
                "session_id": session.id,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at,
                    }
                    for msg in messages
                ],
            }
        )

    return Response(response_data, status=status.HTTP_200_OK)

# check system health
from django.http import JsonResponse
from django.db import connection

def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return JsonResponse({
        "status": "ok",
        "database": db_status,
    })

# additional view with role-based access control


def org_admin_only_view(request, org_id):
    try:
        organization = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return JsonResponse({"detail": "Organization not found"}, status=404)

    if not user_has_role(request.user, organization, [ORG_OWNER, ORG_ADMIN]):
        return JsonResponse({"detail": "Permission denied"}, status=403)

    return JsonResponse({"message": "Access granted"})





def agent_task(request):
    input_text = request.POST.get("input")

    if not input_text:
        return JsonResponse({"detail": "Input required"}, status=400)

    try:
        result = run_agent(TaskAgent, request, input_text)
    except PermissionError as e:
        return JsonResponse({"detail": str(e)}, status=402)

    return JsonResponse({
        "agent": TaskAgent.name,
        "result": result.output,
        "tokens_used": result.tokens_used,
    })




# =========================



def invite_user(request):
    org = request.organization

    if not org or request.org_member.role not in [ORG_OWNER, ORG_ADMIN]:
        return JsonResponse({"detail": "Permission denied"}, status=403)

    email = request.POST.get("email")
    role = request.POST.get("role", "member")

    if not email:
        return JsonResponse({"detail": "Email required"}, status=400)

    invite = OrganizationInvite.objects.create(
        organization=org,
        email=email,
        role=role,
    )

    invite_link = f"http://localhost:8000/api/accept-invite/{invite.token}/"
    print("INVITE LINK:", invite_link)

    return JsonResponse({"message": "Invite created"})





def accept_invite(request, token):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"detail": "Authentication required"},
            status=401,
        )

    try:
        invite = OrganizationInvite.objects.get(token=token)
    except OrganizationInvite.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid invite"},
            status=400,
        )

    if invite.accepted_at is not None:
        return JsonResponse(
            {"detail": "Invite already used"},
            status=400,
        )

    OrganizationMember.objects.get_or_create(
        user=request.user,
        organization=invite.organization,
        defaults={"role": invite.role},
    )

    invite.accepted_at = timezone.now()
    invite.save(update_fields=["accepted_at"])

    return JsonResponse(
        {
            "message": "Successfully joined organization",
            "organization": invite.organization.name,
        }
    )





def agent_workflow(request):
    input_text = request.POST.get("input")

    if not input_text:
        return JsonResponse({"detail": "Input required"}, status=400)

    try:
        result = run_agent(WorkflowAgent, request, input_text)
    except PermissionError as e:
        return JsonResponse({"detail": str(e)}, status=402)

    return JsonResponse({
        "agent": WorkflowAgent.name,
        "result": result.output,
        "tokens_used": result.tokens_used,
    })






