def chunk_text(text: str, chunk_size=400, overlap=80):
    """
    Splits text into overlapping chunks.
    """
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
