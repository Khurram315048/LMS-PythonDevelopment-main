from pathlib import Path

COLLECTION="lms_docs"
DOCS_DIR=Path(__file__).resolve().parent.parent/"docs"
EMBED_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ROLES=("student","teacher","admin","all")
EXTENSIONS={".md",".txt",".html",".htm",".pdf"}

CHUNK_CHARS=700          
TOP_K=5                  
MIN_SCORE=0.40           
MAX_CONTEXT_CHARS=2800   
RERANK_MODEL="Xenova/ms-marco-MiniLM-L-6-v2"   
FETCH_K=20          
RERANK_MIN=-6.5 
RERANK_MARGIN=3.0
