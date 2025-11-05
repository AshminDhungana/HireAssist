from __future__ import annotations

import hashlib
import math
from typing import List, Optional

from app.core.config import settings
from app.services.vector_search import InMemoryVectorSearch


def _hashing_embedding(text: str, dim: int = 256) -> List[float]:
    """Deterministic, fast fallback embedding using hashing buckets."""
    vector = [0.0] * dim
    if not text:
        return vector
    tokens = text.lower().split()
    for tok in tokens:
        h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vector[idx] += 1.0
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def get_embedding(text: str) -> List[float]:
    """Return embedding for text using OpenAI if configured, else hashing fallback."""
    try:
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if api_key:
            # Lazy import to avoid hard dependency
            try:
                from openai import OpenAI  # type: ignore
            except Exception:
                return _hashing_embedding(text)
            client = OpenAI(api_key=api_key)
            resp = client.embeddings.create(model="text-embedding-3-small", input=text or "")
            return list(resp.data[0].embedding)
        return _hashing_embedding(text)
    except Exception:
        return _hashing_embedding(text)


# Module-level vector store singleton
vector_store = InMemoryVectorSearch()
