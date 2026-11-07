import sys
from .indexer import ingest
from .evaluate import run as run_eval
from .retriever import retrieve
from . import store


def main(argv):
    cmd=argv[0] if argv else "ingest"
    if cmd=="ingest":
        ingest(rebuild="--rebuild" in argv)
    elif cmd=="search":
        role=next((a.split("=",1)[1] for a in argv if a.startswith("--role=")),"student")
        question=" ".join(a for a in argv[1:] if not a.startswith("--role="))
        for score,p in retrieve(question,role):
            print(f"{score:.3f} | {p.get('source')} | {p.get('heading')} | {p.get('text','')[:90]!r}")
    elif cmd=="eval":
        run_eval()
    elif cmd=="stats":
        res=store.stats()
        if not res:
            print("Collection nahi mili. Pehle ingest chalao.")
            return
        total,counts=res
        print(f"Total chunks: {total}")
        for (source,role),n in sorted(counts.items(),key=lambda x:(str(x[0][1]),str(x[0][0]))):
            print(f"  {role:8} {source}: {n}")
    else:
        print("Istemal: python -m chatbot.rag [ingest [--rebuild] | search <sawal> [--role=student] | eval | stats]")


main(sys.argv[1:])
