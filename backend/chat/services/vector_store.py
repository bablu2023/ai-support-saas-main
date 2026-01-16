from pathlib import Path
import pickle
import faiss
import numpy as np
from .embeddings import embed_texts

# Backend directory
BASE_DIR = Path.cwd()
VECTOR_DIR = BASE_DIR / "vector_store"


def build_index(org_id: int, documents: list[str]):
    VECTOR_DIR.mkdir(exist_ok=True)

    org_dir = VECTOR_DIR / f"org_{org_id}"
    org_dir.mkdir(parents=True, exist_ok=True)

    vectors = embed_texts(documents)

    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors, dtype="float32"))

    faiss.write_index(index, str(org_dir / "index.faiss"))

    with open(org_dir / "docs.pkl", "wb") as f:
        pickle.dump(documents, f)


def load_index(org_id: int):
    org_dir = VECTOR_DIR / f"org_{org_id}"
    index_path = org_dir / "index.faiss"
    docs_path = org_dir / "docs.pkl"

    if not index_path.exists():
        raise FileNotFoundError(f"No index for org {org_id}")

    index = faiss.read_index(str(index_path))

    with open(docs_path, "rb") as f:
        docs = pickle.load(f)

    return index, docs
