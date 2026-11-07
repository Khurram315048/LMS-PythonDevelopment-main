import uuid
import redis
from . import loader,chunker,embedder,store
from core.config import REDIS_URL


def _bump_version():
    try:
        redis.Redis.from_url(REDIS_URL,socket_connect_timeout=2).incr("docs_version")
    except Exception as e:
        print("Redis version bump skipped:",e)


def build_points():
    docs,skipped=loader.load_documents()
    for s in skipped:
        print("SKIP",s)
    items=[]
    for d in docs:
        n=0
        for page,text in d.pages:
            for heading,body in chunker.sections(text,d.title):
                if page:
                    heading=f"{heading} > page {page}"
                for ch in chunker.chunks(body):
                    items.append((d,n,heading,ch))
                    n+=1
        print(f"{d.key} -> {d.role}: {n} chunks")
    points=[]
    for i in range(0,len(items),32):
        batch=items[i:i+32]
        vectors=embedder.embed([f"{h}\n{ch}" for _,_,h,ch in batch])
        for (d,n,h,ch),v in zip(batch,vectors):
            points.append({
                "id":str(uuid.uuid5(uuid.NAMESPACE_URL,f"{d.key}#{n}")),
                "vector":v,
                "payload":{
                    "source":d.key,
                    "title":d.title,
                    "link":d.link,
                    "role":d.role,
                    "heading":h,
                    "text":ch,
                    "key":d.key
                    }})
    return points,len(docs)


def ingest(rebuild:bool=False):
    points,n_docs=build_points()
    if not points:
        print("No documents index.")
        return
    added,removed=store.sync(points,rebuild=rebuild)
    _bump_version()
    print(f"{n_docs} files, {added} chunks are index, {removed} old chunks have been removed")