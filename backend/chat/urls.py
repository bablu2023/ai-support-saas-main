from django.urls import path
from .views import test_htmx, start_stream, poll_stream
from .views import chat_stream
from .views import chat_ws_page

urlpatterns = [
    path("test-htmx/", test_htmx),
    path("stream/start/", start_stream),
    path("stream/poll/", poll_stream),
    path("stream/", chat_stream, name="chat-stream"),
    path("ws-test/", chat_ws_page),
]



