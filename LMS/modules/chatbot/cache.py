import asyncio
import hashlib
import json
from core.logger  import logging
import time
import uuid
import redis.asyncio as aioredis
from qdrant_client.models import (VectorParams,Distance,PointStruct,Filter,
                                  FieldCondition,MatchValue,Range,PayloadSchemaType)
from core.config import REDIS_URL
from modules.chatbot.rag import store,embedder

TTL=1800
SEM_THRESHOLD=0.92
SEM_COLLECTION="answer_cache"
_r=aioredis.from_url(REDIS_URL,decode_responses=True,socket_connect_timeout=2,socket_timeout=1)
_ready=False


async def _ver()->str:
    return await _r.get("docs_version") or "0"


def _key(ver,role,norm):
    return f"ans:{ver}:{role}:{hashlib.sha1(norm.encode()).hexdigest()}"


async def exact_get(role,norm):
    try:
        raw=await _r.get(_key(await _ver(),role,norm))
        return json.loads(raw) if raw else None
    except Exception as e:
        logging.exception(f"redis get failed: {e}")
        return None


async def exact_set(role,norm,out):
    try:
        await _r.setex(_key(await _ver(),role,norm),TTL,json.dumps(out))
    except Exception as e:
        logging.exception(f"redis set failed: {e}")


def _ensure(dim):
    global _ready
    if _ready:
        return
    c=store.client()
    if not c.collection_exists(SEM_COLLECTION):
        c.create_collection(SEM_COLLECTION,vectors_config=VectorParams(size=dim,distance=Distance.COSINE))
        c.create_payload_index(SEM_COLLECTION,"role",PayloadSchemaType.KEYWORD)
        c.create_payload_index(SEM_COLLECTION,"ver",PayloadSchemaType.KEYWORD)
        c.create_payload_index(SEM_COLLECTION,"ts",PayloadSchemaType.FLOAT)
    _ready=True


def _sem_get(role,vec,ver):
    _ensure(len(vec))
    hits=store.client().query_points(
        SEM_COLLECTION,query=vec,limit=1,with_payload=True,
        query_filter=Filter(must=[
            FieldCondition(key="role",match=MatchValue(value=role)),
            FieldCondition(key="ver",match=MatchValue(value=ver)),
            FieldCondition(key="ts",range=Range(gte=time.time()-TTL)),
        ])).points
    if not hits:
        return 0.0,None
    return hits[0].score,json.loads(hits[0].payload["out"])


def _sem_set(role,vec,ver,out):
    _ensure(len(vec))
    store.client().upsert(SEM_COLLECTION,points=[PointStruct(
        id=str(uuid.uuid4()),vector=vec,
        payload={"role":role,"ver":ver,"ts":time.time(),"out":json.dumps(out)})])


async def embed(text):
    return (await asyncio.to_thread(embedder.embed,[text]))[0]


async def sem_get(role,vec):
    try:
        ver=await _ver()
        score,out=await asyncio.to_thread(_sem_get,role,vec,ver)
        logging.info(f"SEM best score={score:.3f}")
        return out if score>=SEM_THRESHOLD else None
    except Exception:
        logging.exception("semantic cache get failed")
        return None


async def sem_set(role,vec,out):
    try:
        ver=await _ver()
        await asyncio.to_thread(_sem_set,role,vec,ver,out)
    except Exception:
        logging.exception("semantic cache set failed")


async def rate_ok(uid:int,limit:int=20,window:int=60)->bool:
    try:
        k=f"rl:{uid}:{int(time.time()//window)}"
        n=await _r.incr(k)
        if n==1:
            await _r.expire(k,window)
        return n<=limit
    except Exception:
        logging.exception("rate limiter failed")
        return True      