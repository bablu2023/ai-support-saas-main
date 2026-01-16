from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from organizations.models import Organization
from organizations.utils import generate_widget_snippet

from billing.enforcement import enforce_token_limit, UsageLimitExceeded


from chat.services.retrieval import rag_chat
from chat.models import ChatSession, ChatMessage

from knowledge.services.ingestion import ingest_plain_text


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
