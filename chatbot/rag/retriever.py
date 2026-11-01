import logging
from . import embedder,store
from .settings import ROLES,TOP_K,MIN_SCORE,MAX_CONTEXT_CHARS

NOT_FOUND=("No matching document found. Say you do not have this information "
           "and tell the user to ask the office.")


def retrieve(question:str,role:str):
    vec=embedder.embed([question])[0]
    return [(h.score,h.payload) for h in store.search(vec,[role,"all"],TOP_K)]


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
    passages,seen,used=[],set(),0
    for score,p in hits:
        if score<MIN_SCORE:
            continue
        text=p.get("text","")
        key=(p.get("source"),text)
        if key in seen:
            continue
        if passages and used+len(text)>MAX_CONTEXT_CHARS:
            break
        seen.add(key)
        used+=len(text)
        passages.append({"source":p.get("source"),"heading":p.get("heading",""),"text":text})
    if not passages:
        return {"passages":[],"note":NOT_FOUND}
    return {"passages":passages}
