import uuid
from pathlib import Path
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (VectorParams,Distance,PointStruct,
                                  Filter,FieldCondition,MatchAny,PayloadSchemaType)
from config import QDRANT_URL,QDRANT_API_KEY

COLLECTION="lms_docs"
DOCS=Path(__file__).parent/"docs"
MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MIN_SCORE=0.30
TOP_K=4

_embedder=None
_client=None


def _embed(texts):
    global _embedder
    if _embedder is None:
        _embedder=TextEmbedding(MODEL)
    return [v.tolist() for v in _embedder.embed(texts)]


def _qdrant():
    global _client
    if _client is None:
        _client=QdrantClient(url=QDRANT_URL,api_key=QDRANT_API_KEY,timeout=20)
    return _client


def _chunks(text,limit=600):
    out,cur=[],""
    for block in text.split("\n\n"):
        block=block.strip()
        if not block:
            continue
        if cur and len(cur)+len(block)>limit:
            out.append(cur)
            cur=""
        cur=(cur+"\n\n"+block).strip()
    if cur:
        out.append(cur)
    return out


def ingest():
    files=sorted(DOCS.glob("*.md"))
    points=[]
    for f in files:
        raw=f.read_text(encoding="utf-8-sig").strip()
        if not raw.lower().startswith("role:"):
            print(f"SKIP {f.name}: pehli line 'role: student' ya 'role: teacher' ya 'role: all' honi chahiye")
            continue
        first,_,raw=raw.partition("\n")
        role=first.split(":",1)[1].strip().lower()
        if role not in ("student","teacher","all"):
            print(f"SKIP {f.name}: ghalat role '{role}'")
            continue
        print(f"{f.name} -> {role}")
        for i,ch in enumerate(_chunks(raw)):
            points.append((f.stem,role,i,ch))
    # for f in files:
    #     raw=f.read_text(encoding="utf-8").strip()
    #     print(f"SKIP {f.name}: pehli line 'role: student' ya 'role: teacher' ya 'role: all' honi chahiye")
    #     # role="all"
    #     pass
    #     if raw.lower().startswith("role:"):
    #         first,_,raw=raw.partition("\n")
    #         role=first.split(":",1)[1].strip().lower() or "all"
    #     for i,ch in enumerate(_chunks(raw)):
    #         points.append((f.stem,role,i,ch))
    if not points:
        print("Koi document nahi mila")
        return
    vectors=_embed([p[3] for p in points])
    q=_qdrant()
    if q.collection_exists(COLLECTION):
        q.delete_collection(COLLECTION)
    q.create_collection(COLLECTION,vectors_config=VectorParams(size=len(vectors[0]),distance=Distance.COSINE))
    q.create_payload_index(COLLECTION,"role",PayloadSchemaType.KEYWORD)
    q.upsert(COLLECTION,points=[
        PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL,f"{s}-{i}")),vector=v,
                    payload={"source":s,"role":r,"text":t})
        for (s,r,i,t),v in zip(points,vectors)])
    print(f"{len(files)} files, {len(points)} chunks index ho gaye")


def search_policies(user:dict,question=None):
    question=str(question or "").strip()[:300]
    if not question:
        return {"passages":[],"note":"No question given"}
    vec=_embed([question])[0]
    res=_qdrant().query_points(
        COLLECTION,query=vec,limit=TOP_K,
        query_filter=Filter(must=[FieldCondition(key="role",match=MatchAny(any=[user["role"],"all"]))]),
        with_payload=True).points
    passages=[{"source":p.payload["source"],"text":p.payload["text"]} for p in res if p.score>=MIN_SCORE]
    if not passages:
        return {"passages":[],"note":"No matching document found. Say you do not have this information and tell the user to ask the office."}
    return {"passages":passages}


if __name__=="__main__":
    ingest()