import os
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_texts(texts: list[str]):
    """
    Uses OpenAI embeddings (NO local ML, NO DLL issues)
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    return np.array([e.embedding for e in response.data], dtype="float32")
