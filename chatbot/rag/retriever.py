import logging
from . import embedder,store,reranker
from .settings import (ROLES,TOP_K,MIN_SCORE,MAX_CONTEXT_CHARS,
                       FETCH_K,RERANK_MODEL,RERANK_MIN,RERANK_MARGIN)

NOT_FOUND=("No matching document found. Say you do not have this information "
           "and tell the user to ask the office.")


def retrieve(question:str,role:str):
    vec=embedder.embed([question])[0]
    hits=store.search(vec,[role,"all"],FETCH_K if RERANK_MODEL else TOP_K)
    items=[(h.score,h.payload) for h in hits]
    if RERANK_MODEL and items:
        try:
            return reranker.rerank(question,items)[:TOP_K]
        except Exception:
            logging.exception("rerank failed, using dense scores")
    return [(s,{**p,"_scorer":"dense"}) for s,p in items][:TOP_K]


def passes(score:float,p:dict)->bool:
    limit=RERANK_MIN if p.get("_scorer")=="rerank" else MIN_SCORE
    return score>=limit


def search_policies(user:dict,question=None):
    question=str(question or "").strip()[:300]
    if not question:
        return {"passages":[],"note":"No question given"}
    role=str(user.get("role") or "")
    if role not in ROLES or role=="all":
        return {"passages":[],"note":NOT_FOUND}
    try:
        hits=retrieve(question,role)
    except Exception:
        logging.exception("RAG search failed")
        return {"error":"document search unavailable"}
    top=hits[0][0] if hits else 0
    passages,seen,used=[],set(),0
    for score,p in hits:
        if not passes(score,p):
            continue
        scorer=p.get("_scorer")
        if scorer=="rerank" and score<top-RERANK_MARGIN:
            continue
        text=p.get("text","")
        key=(p.get("source"),text)
        if key in seen:
            continue
        if passages and used+len(text)>MAX_CONTEXT_CHARS:
            break
        seen.add(key)
        used+=len(text)
        passages.append({"source":p.get("source"),"heading":p.get("heading",""),
                         "title":p.get("title",""),"link":p.get("link",""),
                         "score":round(score,3),"scorer":scorer,"text":text})
    if not passages:
        return {"passages":[],"note":NOT_FOUND}
    return {"passages":passages}