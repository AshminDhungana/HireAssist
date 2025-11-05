from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.core.security import decode_token
from app.services.embeddings import get_embedding, vector_store


router = APIRouter()


def require_auth(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    try:
        scheme, token = authorization.split()
        assert scheme.lower() == "bearer"
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


class UpsertItem(BaseModel):
    id: str
    text: str
    metadata: Dict = {}


class UpsertRequest(BaseModel):
    namespace: str
    items: List[UpsertItem]


@router.post("/vectors/upsert")
def upsert_vectors(payload: UpsertRequest, authorization: str = Header(None)):
    require_auth(authorization)
    vectors = []
    for it in payload.items:
        emb = get_embedding(it.text[:5000])
        vectors.append((it.id, emb, it.metadata))
    vector_store.upsert(payload.namespace, vectors)
    return {"success": True, "upserted": len(vectors)}


class QueryRequest(BaseModel):
    namespace: str
    text: str
    top_k: int = 10
    filter: Optional[Dict] = None


@router.post("/vectors/query")
def query_vectors(payload: QueryRequest, authorization: str = Header(None)):
    require_auth(authorization)
    emb = get_embedding(payload.text[:5000])
    results = vector_store.query(payload.namespace, emb, top_k=payload.top_k, filter=payload.filter)
    return {"results": results}


