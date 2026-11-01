from pathlib import Path

COLLECTION="lms_docs"
DOCS_DIR=Path(__file__).resolve().parent.parent/"docs"
EMBED_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ROLES=("student","teacher","admin","all")
EXTENSIONS={".md",".txt",".html",".htm",".pdf"}

CHUNK_CHARS=700          
TOP_K=5                  
MIN_SCORE=0.30           
MAX_CONTEXT_CHARS=2800   
