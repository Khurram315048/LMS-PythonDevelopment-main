from qdrant_client import QdrantClient
from qdrant_client.models import (VectorParams,Distance,PointStruct,PointIdsList,
                                  Filter,FieldCondition,MatchAny,PayloadSchemaType)
from config import QDRANT_URL,QDRANT_API_KEY
from .settings import COLLECTION

_client=None


def client():
    global _client
    if _client is None:
        if not QDRANT_URL:
            raise RuntimeError("QDRANT_URL .env mein nahi hai")
        _client=QdrantClient(url=QDRANT_URL,api_key=QDRANT_API_KEY,timeout=20)
    return _client


def _existing_ids(c):
    ids,offset=set(),None
    while True:
        recs,offset=c.scroll(COLLECTION,limit=256,offset=offset,with_payload=False,with_vectors=False)
        ids.update(str(r.id) for r in recs)
        if offset is None:
            return ids


def sync(points:list,rebuild:bool=False):
    
    c=client()
    if rebuild and c.collection_exists(COLLECTION):
        c.delete_collection(COLLECTION)
    if not c.collection_exists(COLLECTION):
        c.create_collection(COLLECTION,vectors_config=VectorParams(size=len(points[0]["vector"]),distance=Distance.COSINE))
        for field in ("role","source"):
            c.create_payload_index(COLLECTION,field,PayloadSchemaType.KEYWORD)
    old=_existing_ids(c)
    for i in range(0,len(points),64):
        c.upsert(COLLECTION,points=[PointStruct(id=p["id"],vector=p["vector"],payload=p["payload"])
                                    for p in points[i:i+64]])
    stale=list(old-{p["id"] for p in points})
    if stale:
        c.delete(COLLECTION,points_selector=PointIdsList(points=stale))
    return len(points),len(stale)


def search(vector,roles:list,limit:int):
    return client().query_points(
        COLLECTION,query=vector,limit=limit,
        query_filter=Filter(must=[FieldCondition(key="role",match=MatchAny(any=roles))]),
        with_payload=True).points


def stats():
    c=client()
    if not c.collection_exists(COLLECTION):
        return None
    counts,offset={},None
    while True:
        recs,offset=c.scroll(COLLECTION,limit=256,offset=offset,with_payload=["source","role"],with_vectors=False)
        for r in recs:
            k=(r.payload.get("source"),r.payload.get("role"))
            counts[k]=counts.get(k,0)+1
        if offset is None:
            break
    return sum(counts.values()),counts
