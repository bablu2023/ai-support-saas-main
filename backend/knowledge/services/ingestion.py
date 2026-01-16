import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from knowledge.models import KnowledgeSource, KnowledgeChunk

# 🔑 Backend root
BASE_DIR = Path.cwd()
VECTOR_ROOT = BASE_DIR / "vector_store"

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY")
)


def get_vector_store(org_id: int):
    """
    Load FAISS for an organization if exists.
    """
    org_dir = VECTOR_ROOT / f"org_{org_id}"
    if org_dir.exists():
        return FAISS.load_local(
            org_dir,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return None


def save_vector_store(store, org_id: int):
    org_dir = VECTOR_ROOT / f"org_{org_id}"
    org_dir.mkdir(parents=True, exist_ok=True)
    store.save_local(org_dir)


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    return splitter.split_text(text)


def ingest_plain_text(*, organization, title, text):
    """
    SAFE, MULTI-TENANT INGESTION
    """

    VECTOR_ROOT.mkdir(exist_ok=True)

    source = KnowledgeSource.objects.create(
        organization=organization,
        source_type="text",
        title=title,
        content=text
    )

    chunks = chunk_text(text)

    store = get_vector_store(organization.id)

    # First-time FAISS creation
    if store is None:
        store = FAISS.from_texts(
            texts=[chunks[0]],
            embedding=embeddings,
            metadatas=[{
                "org_id": organization.id,
                "source_id": source.id
            }]
        )
        start_index = 1
    else:
        start_index = 0

    # Add remaining chunks
    if chunks[start_index:]:
        store.add_texts(
            texts=chunks[start_index:],
            metadatas=[{
                "org_id": organization.id,
                "source_id": source.id
            }] * len(chunks[start_index:])
        )

    # Persist chunks in DB (audit, UI, reindexing)
    for chunk in chunks:
        KnowledgeChunk.objects.create(
            organization=organization,
            source=source,
            text=chunk,
            embedding_id="faiss"
        )

    save_vector_store(store, organization.id)
