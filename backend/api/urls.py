from django.urls import path
from .views import (
    chat_api,
    widget_snippet,
    upload_text_knowledge,
    chat_logs,
)

urlpatterns = [
    path("chat/", chat_api),
    path("chat/logs/", chat_logs),
    path("widget/snippet/", widget_snippet),
    path("knowledge/text/", upload_text_knowledge),
]




