import os
from openai import OpenAI

from chat.services.vector_store import load_index
from chat.services.embeddings import embed_texts

from billing.tokens import estimate_tokens
from billing.enforcement import enforce_token_limit, UsageLimitExceeded
from billing.models import TokenUsage

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def rag_chat(organization, user_id, query):
    """
    Non-streaming RAG (used by API)
    """
    try:
        index, docs = load_index(organization.id)

        query_vec = embed_texts([query])
        scores, indices = index.search(query_vec, k=3)

        valid_indices = [
            i for i in indices[0]
            if i != -1 and i < len(docs)
        ]

        context = "\n\n".join(docs[i] for i in valid_indices)

        if not context.strip():
            return "No relevant knowledge found."

        prompt_text = f"{context}\n\n{query}"
        prompt_tokens = estimate_tokens(prompt_text)

        # 🔐 enforce BEFORE spending
        enforce_token_limit(organization, prompt_tokens)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a support AI. "
                        "Answer ONLY using the provided context. "
                        "If the answer is not in the context, say you don't know."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt_text,
                },
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()
        completion_tokens = estimate_tokens(answer)

        TokenUsage.objects.create(
            organization=organization,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

        return answer

    except UsageLimitExceeded:
        return "🚫 Monthly token limit reached. Please upgrade your plan."

    except FileNotFoundError:
        return "Knowledge base is empty. Please upload documents first."

    except Exception as e:
        print("RAG ERROR:", e)
        return "AI service temporarily unavailable."


def rag_chat_stream(organization, user_id, query):
    """
    Streaming RAG (SSE / WebSocket)
    """
    try:
        index, docs = load_index(organization.id)

        query_vec = embed_texts([query])
        scores, indices = index.search(query_vec, k=3)

        valid_indices = [
            i for i in indices[0]
            if i != -1 and i < len(docs)
        ]

        context = "\n\n".join(docs[i] for i in valid_indices)

        if not context.strip():
            yield "No relevant knowledge found."
            return

        prompt_text = f"{context}\n\n{query}"
        prompt_tokens = estimate_tokens(prompt_text)

        enforce_token_limit(organization, prompt_tokens)

        TokenUsage.objects.create(
            organization=organization,
            prompt_tokens=prompt_tokens,
            completion_tokens=0,
            total_tokens=prompt_tokens,
        )

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a support AI. "
                        "Answer ONLY using the provided context."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt_text,
                },
            ],
            temperature=0.2,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                text = delta.content
                yield text

                tokens = estimate_tokens(text)
                TokenUsage.objects.create(
                    organization=organization,
                    prompt_tokens=0,
                    completion_tokens=tokens,
                    total_tokens=tokens,
                )

    except UsageLimitExceeded:
        yield "🚫 Monthly token limit reached. Please upgrade your plan."

    except FileNotFoundError:
        yield "Knowledge base is empty. Please upload documents first."

    except Exception as e:
        print("STREAM RAG ERROR:", e)
        yield "AI service temporarily unavailable."
