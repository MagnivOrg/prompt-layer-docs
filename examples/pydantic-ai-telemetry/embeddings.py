from __future__ import annotations

"""Small native Pydantic AI embeddings demo used by the chat agent."""

import os
from collections.abc import Sequence

from pydantic import BaseModel, Field
from pydantic_ai import Embedder


DEFAULT_EMBEDDING_MODEL = "openai:text-embedding-3-small"


class DemoKnowledgeItem(BaseModel):
    id: str
    title: str
    text: str


class EmbeddingSearchResult(BaseModel):
    query: str
    matched_item: DemoKnowledgeItem
    similarity: float = Field(ge=-1, le=1)
    embedding_model: str
    embedded_document_count: int


DEMO_KNOWLEDGE_ITEMS = (
    DemoKnowledgeItem(
        id="telemetry",
        title="OpenTelemetry export",
        text=(
            "This app configures Pydantic AI instrumentation and exports "
            "OpenTelemetry traces to PromptLayer through OTLP."
        ),
    ),
    DemoKnowledgeItem(
        id="weather_tool",
        title="Weather tool",
        text=(
            "The weather tool is an agent tool that adds PromptLayer prompt "
            "metadata to the current span and returns demo weather."
        ),
    ),
    DemoKnowledgeItem(
        id="embeddings",
        title="Embedding search",
        text=(
            "Embedding search converts text into vectors, compares vectors with "
            "cosine similarity, and finds semantically related content."
        ),
    ),
)


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    """Create the instrumented embedder lazily so env vars load before use."""
    global _embedder

    if _embedder is None:
        _embedder = Embedder(
            os.getenv("PYDANTIC_AI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
            instrument=True,
        )

    return _embedder


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0
    return dot_product / (left_norm * right_norm)


async def search_demo_embeddings(query: str) -> EmbeddingSearchResult:
    """Embed the query and local demo topics, then return the closest topic."""
    embedder = get_embedder()
    query_result = await embedder.embed_query(query)
    documents_result = await embedder.embed_documents([item.text for item in DEMO_KNOWLEDGE_ITEMS])
    query_embedding = query_result.embeddings[0]

    scored_items = [
        (cosine_similarity(query_embedding, document_embedding), item)
        for item, document_embedding in zip(DEMO_KNOWLEDGE_ITEMS, documents_result.embeddings)
    ]
    similarity, matched_item = max(scored_items, key=lambda scored_item: scored_item[0])

    return EmbeddingSearchResult(
        query=query,
        matched_item=matched_item,
        similarity=similarity,
        embedding_model=query_result.model_name,
        embedded_document_count=len(DEMO_KNOWLEDGE_ITEMS),
    )
