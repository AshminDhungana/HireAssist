from __future__ import annotations

from typing import List, Tuple, Optional, Protocol, Dict
from app.core.config import settings


class VectorSearchClient(Protocol):
    """Protocol for vector search backends."""

    def upsert(self, namespace: str, items: List[Tuple[str, List[float], Dict]]) -> None:
        """
        Upsert items into a namespace.
        Each item is (id, embedding_vector, metadata_dict).
        """
        ...

    def query(self, namespace: str, vector: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        """Return top_k most similar items as a list of {id, score, metadata}."""
        ...

    def delete(self, namespace: str, ids: Optional[List[str]] = None) -> None:
        """Delete specific ids or entire namespace if ids is None."""
        ...


class InMemoryVectorSearch:
    """Simple in-memory vector store for development and tests."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Tuple[List[float], Dict]]] = {}

    def upsert(self, namespace: str, items: List[Tuple[str, List[float], Dict]]) -> None:
        space = self._store.setdefault(namespace, {})
        for item_id, vec, meta in items:
            space[item_id] = (vec, meta)

    def query(self, namespace: str, vector: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        import math

        def cosine_similarity(a: List[float], b: List[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)

        space = self._store.get(namespace, {})
        results = []
        for item_id, (vec, meta) in space.items():
            if filter:
                # Naive AND filter on metadata
                if not all(meta.get(k) == v for k, v in filter.items()):
                    continue
            score = cosine_similarity(vector, vec)
            results.append({"id": item_id, "score": score, "metadata": meta})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    def delete(self, namespace: str, ids: Optional[List[str]] = None) -> None:
        if namespace not in self._store:
            return
        if ids is None:
            del self._store[namespace]
        else:
            for _id in ids:
                self._store[namespace].pop(_id, None)


class PineconeAdapter:
    """Pinecone adapter (lazy import; only used when selected)."""

    def __init__(self, api_key: Optional[str], environment: Optional[str], index_name: Optional[str]) -> None:
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name or "hireassist"
        self._pc = None
        self._index = None

    def _ensure(self):
        if self._index is not None:
            return
        try:
            from pinecone import Pinecone
        except Exception as e:
            raise RuntimeError("Pinecone SDK not installed") from e
        if not self.api_key:
            raise RuntimeError("Pinecone API key missing")
        self._pc = Pinecone(api_key=self.api_key)
        self._index = self._pc.Index(self.index_name)

    def upsert(self, namespace: str, items: List[Tuple[str, List[float], Dict]]) -> None:
        self._ensure()
        vectors = [{"id": _id, "values": vec, "metadata": meta} for _id, vec, meta in items]
        self._index.upsert(vectors=vectors, namespace=namespace)

    def query(self, namespace: str, vector: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        self._ensure()
        resp = self._index.query(vector=vector, top_k=top_k, include_metadata=True, namespace=namespace, filter=filter)
        return [{"id": m.id, "score": m.score, "metadata": dict(m.metadata or {})} for m in resp.matches]

    def delete(self, namespace: str, ids: Optional[List[str]] = None) -> None:
        self._ensure()
        if ids is None:
            self._index.delete(delete_all=True, namespace=namespace)
        else:
            self._index.delete(ids=ids, namespace=namespace)


class QdrantAdapter:
    """Qdrant adapter (lazy import; only used when selected)."""

    def __init__(self, url: Optional[str], api_key: Optional[str]) -> None:
        self.url = url or "http://localhost:6333"
        self.api_key = api_key
        self._client = None

    def _ensure(self):
        if self._client is not None:
            return
        try:
            from qdrant_client import QdrantClient
        except Exception as e:
            raise RuntimeError("qdrant-client not installed") from e
        self._client = QdrantClient(url=self.url, api_key=self.api_key)

    def upsert(self, namespace: str, items: List[Tuple[str, List[float], Dict]]) -> None:
        self._ensure()
        from qdrant_client.models import PointStruct
        points = [PointStruct(id=_id, vector=vec, payload=meta) for _id, vec, meta in items]
        self._client.upsert(collection_name=namespace, points=points)

    def query(self, namespace: str, vector: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        self._ensure()
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        q_filter = None
        if filter:
            q_filter = Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter.items()])
        resp = self._client.search(collection_name=namespace, query_vector=vector, limit=top_k, query_filter=q_filter, with_payload=True)
        return [{"id": str(r.id), "score": float(r.score), "metadata": dict(r.payload or {})} for r in resp]

    def delete(self, namespace: str, ids: Optional[List[str]] = None) -> None:
        self._ensure()
        if ids is None:
            self._client.delete_collection(collection_name=namespace)
        else:
            self._client.delete(collection_name=namespace, points_selector=ids)


def get_vector_store() -> VectorSearchClient:
    backend = (settings.VECTOR_BACKEND or "inmemory").lower()
    if backend == "pinecone":
        return PineconeAdapter(settings.PINECONE_API_KEY, settings.PINECONE_ENVIRONMENT, settings.PINECONE_INDEX)
    if backend == "qdrant":
        return QdrantAdapter(settings.QDRANT_URL, settings.QDRANT_API_KEY)
    return InMemoryVectorSearch()


