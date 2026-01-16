import time

def fake_stream(text, chunk_size=15, delay=0.2):
    """
    Simulate streaming by yielding chunks of text.
    Replace later with real LLM streaming.
    """
    for i in range(0, len(text), chunk_size):
        yield text[: i + chunk_size]
        time.sleep(delay)
