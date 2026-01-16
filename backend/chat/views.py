from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from organizations.models import Organization
from .models import ChatSession, ChatMessage
from chat.services.retrieval import rag_chat


from django.http import StreamingHttpResponse
from chat.services.retrieval import rag_chat_stream
from .jwt import create_jwt




@require_http_methods(["GET", "POST"])
def test_htmx(request):
    # Ensure an organization exists (dev-safe)
    organization, _ = Organization.objects.get_or_create(
        name="Default Organization"
    )

    session, _ = ChatSession.objects.get_or_create(
        organization=organization,
        user_identifier="htmx_test_user",
    )

    if request.method == "POST":
        user_message = request.POST.get("message")

        if user_message:
            ChatMessage.objects.create(
                session=session,
                content=user_message,
                role="user",
            )

            ai_answer = rag_chat(
                organization=organization,
                user_id=session.user_identifier,
                query=user_message,
            ) or "⚠️ AI did not return a response."

            ChatMessage.objects.create(
                session=session,
                content=str(ai_answer),
                role="assistant",
            )

        return render(
            request,
            "partials/chat/messages.html",
            {
                "messages": session.messages.order_by("id")
            },
        )

    return render(
        request,
        "pages/chat.html",
        {
            "session": session,
            "messages": session.messages.order_by("id"),
        },
    )


def start_stream(request):
    return JsonResponse({"status": "not implemented yet"})


def poll_stream(request):
    return JsonResponse({"status": "not implemented yet"})

def chat_stream(request):
    org = Organization.objects.first()
    user_id = request.user.username if request.user.is_authenticated else "anon"
    query = request.GET.get("message", "")

    def event_stream():
        for chunk in rag_chat_stream(org, user_id, query):
            yield f"data: {chunk}\n\n"   # 🔥 SSE format

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream"
    )



def chat_ws_page(request):
    return render(request, "pages/chat_ws.html")





def chat_ws_page(request):
    org = Organization.objects.first()

    token = create_jwt({
        "user_id": request.user.id if request.user.is_authenticated else None,
        "org_id": org.id,
    })

    return render(request, "pages/chat_ws.html", {
        "jwt_token": token
    })

