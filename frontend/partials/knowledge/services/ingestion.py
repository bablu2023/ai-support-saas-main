from chat.services.vector_store import build_index
from knowledge.models import KnowledgeDocument


def ingest_plain_text(*, organization, title, text):
    print("INGESTION CALLED FOR ORG:", organization.id)

    KnowledgeDocument.objects.create(
        organization=organization,
        title=title,
        content=text,
    )

    docs = KnowledgeDocument.objects.filter(
        organization=organization
    ).values_list("content", flat=True)

    build_index(
        org_id=organization.id,
        documents=list(docs),
    )
