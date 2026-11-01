import json
from pathlib import Path
from .retriever import retrieve
from .settings import MIN_SCORE

CASES=Path(__file__).with_name("eval_cases.json")


def run():
    cases=json.loads(CASES.read_text(encoding="utf-8"))
    hit1=hitk=0
    rr=0.0
    for c in cases:
        hits=[p["source"] for s,p in retrieve(c["question"],c.get("role","student")) if s>=MIN_SCORE]
        want=c["source"]
        found=want in hits
        hit1+=bool(hits) and hits[0]==want
        hitk+=found
        rr+=1/(hits.index(want)+1) if found else 0
        print(("OK  " if found else "MISS"),c["question"],"->",hits)
    n=len(cases)
    print(f"Hit@1 {hit1}/{n}   Hit@K {hitk}/{n}   MRR {rr/n:.2f}")
