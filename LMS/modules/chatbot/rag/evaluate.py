import json
from pathlib import Path
from .retriever import retrieve
from .settings import MIN_SCORE
from .retriever import retrieve,passes


CASES=Path(__file__).with_name("eval_cases.json")


def _norm(s):
    return str(s or "").replace("\\","/").lower().rsplit(".",1)[0]


def _match(got,want):
    g,w=_norm(got),_norm(want)
    return g==w or ("/" not in w and g.split("/")[-1]==w)


def run():
    cases=json.loads(CASES.read_text(encoding="utf-8"))
    pos=[c for c in cases if c.get("source")]
    neg=[c for c in cases if not c.get("source")]
    hit1=hitk=0
    rr=0.0
    want_scores,neg_scores=[],[]

    for c in pos:
        raw=retrieve(c["question"],c.get("role","student"))
        hits=[]
        for s,p in raw:
            if passes(s,p) and p["source"] not in hits:
            # if s>=MIN_SCORE and p["source"] not in hits:
                hits.append(p["source"])
        idx=next((i for i,h in enumerate(hits) if _match(h,c["source"])),None)
        best=max((s for s,p in raw if _match(p["source"],c["source"])),default=0.0)
        want_scores.append(best)
        if idx is not None:
            hitk+=1
            hit1+=idx==0
            rr+=1/(idx+1)
        status="OK  " if idx is not None else "MISS"
        note="" if idx is not None else f"  (wanted doc score {best:.2f}, MIN_SCORE {MIN_SCORE})"
        print(f"{status} [{c.get('role','student')}] {c['question']} -> {hits}{note}")
        print("      ",[(round(s,1),p["source"].split("/")[-1]) for s,p in raw[:4]])

    rejected=0
    for c in neg:
        raw=retrieve(c["question"],c.get("role","student"))
        top=raw[0][0] if raw else 0.0
        neg_scores.append(top)
        ok=not (raw and passes(raw[0][0],raw[0][1]))
        # ok=top<MIN_SCORE
        rejected+=ok
        print(f"{'OK  ' if ok else 'LEAK'} [{c.get('role','student')}] {c['question']} -> top score {top:.2f} (should be below {MIN_SCORE})")

    n=len(pos)
    print()
    if n:
        print(f"Hit@1 {hit1}/{n}   Hit@K {hitk}/{n}   MRR {rr/n:.2f}")
        print(f"Wanted-doc score: lowest {min(want_scores):.2f}")
    if neg:
        print(f"Negative cases rejected {rejected}/{len(neg)}   highest negative score {max(neg_scores):.2f}")
    if n and neg:
        lo,hi=max(neg_scores),min(want_scores)
        if lo<hi:
            print(f"MIN_SCORE can be between {lo:.2f} and {hi:.2f}")
        else:
            print("Scores overlap: no single MIN_SCORE separates them. Improve docs or use a reranker.")