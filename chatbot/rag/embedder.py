import threading
from fastembed import TextEmbedding
from .settings import EMBED_MODEL

_lock=threading.Lock()
_model=None


def embed(texts):
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model=TextEmbedding(EMBED_MODEL)
    return [v.tolist() for v in _model.embed(texts)]
