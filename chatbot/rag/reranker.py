import threading
from fastembed.rerank.cross_encoder import TextCrossEncoder
from .settings import RERANK_MODEL

_lock=threading.Lock()
_model=None


def _get():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model=TextCrossEncoder(model_name=RERANK_MODEL)
    return _model


def rerank(question:str,items:list)->list:
    """items = [(dense_score,payload)]. Return [(rerank_score,payload)] best first."""
    docs=[f"{p.get('heading','')}\n{p.get('text','')}" for _,p in items]
    scores=list(_get().rerank(question,docs))
    out=[(float(s),{**p,"_scorer":"rerank","_dense":round(d,3)})
         for s,(d,p) in zip(scores,items)]
    out.sort(key=lambda x:x[0],reverse=True)
    return out