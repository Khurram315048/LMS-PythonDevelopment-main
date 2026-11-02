import re

from chatbot.rag.settings import RERANK_MARGIN



def collect_sources(passages,margin:float=0.10,max_docs:int=2)->list:
    items=[p for p in passages or [] if isinstance(p,dict)]
    if not items:
        return []
    items.sort(key=lambda p:p.get("score") or 0,reverse=True)
    top=items[0].get("score") or 0
    if items[0].get("scorer")=="rerank":
        margin=RERANK_MARGIN
    out,seen,seen_links=[],set(),set()
    for p in items:
        if (p.get("score") or 0)<top-margin:
            continue
        stem=str(p.get("source") or "").strip()
        if not stem:
            continue
        heading=str(p.get("heading") or "").strip()
        link=p.get("link") or None
        if (stem,heading) in seen or (link and link in seen_links):
            continue
        seen.add((stem,heading))
        if link:
            seen_links.add(link)
        name=stem.replace("\\","/").split("/")[-1].rsplit(".",1)[0]
        title=p.get("title") or re.sub(r"[_\-]+"," ",name).title()
        out.append({"title":title,"heading":heading,"doc":stem,"link":link})
        if len(out)>=max_docs:
            break
    return out