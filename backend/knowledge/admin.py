from django.contrib import admin
from .models import KnowledgeSource, KnowledgeChunk

@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ("organization", "title", "source_type", "created_at")
    search_fields = ("title",)
    list_filter = ("organization", "source_type")

@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ("organization", "source", "created_at")
    search_fields = ("content",)


