from django.db import models
from organizations.models import Organization


class KnowledgeSource(models.Model):
    SOURCE_TYPES = (
        ("url", "Website URL"),
        ("text", "Plain Text"),
        ("document", "Document"),
        ("faq", "FAQ"),
        ("qa", "Manual Q&A"),
    )

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="knowledge_sources"
    )
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Raw extracted text")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} | {self.source_type} | {self.title}"


class KnowledgeChunk(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    source = models.ForeignKey(KnowledgeSource, on_delete=models.CASCADE)
    text = models.TextField()
    embedding_id = models.CharField(
        max_length=255, help_text="Vector DB reference id"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.id} ({self.source.title})"

