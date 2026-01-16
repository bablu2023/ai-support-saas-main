from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "user_identifier", "started_at")
    readonly_fields = ("organization", "user_identifier", "started_at")
    list_filter = ("organization",)
    search_fields = ("user_identifier",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "created_at")
    readonly_fields = ("session", "role", "content", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)




