from __future__ import annotations

from typing import List, Tuple, Optional, Protocol, Dict


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
    """Stub adapter for Pinecone. Not enabled by default."""

    def __init__(self, api_key: Optional[str] = None, index_name: Optional[str] = None) -> None:
        self.api_key = api_key
        self.index_name = index_name

    def upsert(self, namespace: str, items: List[Tuple[str, List[float], Dict]]) -> None:
        raise NotImplementedError("Pinecone integration is not enabled in this environment")

    def query(self, namespace: str, vector: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        raise NotImplementedError("Pinecone integration is not enabled in this environment")

    def delete(self, namespace: str, ids: Optional[List[str]] = None) -> None:
        raise NotImplementedError("Pinecone integration is not enabled in this environment")


class QdrantAdapter:
    """Stub adapter for Qdrant. Not enabled by default."""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.url = url
        self.api_key = api_key

    def upsert(self, namespace: str, items: List[Tuple[str, List[float], Dict]]) -> None:
        raise NotImplementedError("Qdrant integration is not enabled in this environment")

    def query(self, namespace: str, vector: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        raise NotImplementedError("Qdrant integration is not enabled in this environment")

    def delete(self, namespace: str, ids: Optional[List[str]] = None) -> None:
        raise NotImplementedError("Qdrant integration is not enabled in this environment")


