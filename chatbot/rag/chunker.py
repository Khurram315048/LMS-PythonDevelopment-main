import re
from .settings import CHUNK_CHARS

_PIECES=re.compile(r"(?<=[.!?])\s+|\n")


def sections(text:str,fallback_title:str):
    h1,h2="",""
    buf,out=[],[]

    def flush():
        body="\n".join(buf).strip()
        if body:
            path=" > ".join(x for x in (h1 or fallback_title,h2) if x)
            out.append((path,body))

    for line in text.splitlines():
        if line.startswith("# "):
            flush()
            buf.clear()
            h1,h2=line[2:].strip(),""
        elif line.startswith("## "):
            flush()
            buf.clear()
            h2=line[3:].strip()
        else:
            buf.append(line)
    flush()
    return out


def _units(block:str,limit:int):
    if len(block)<=limit:
        return [block]
    out=[]
    for piece in _PIECES.split(block):
        piece=piece.strip()
        while len(piece)>limit:
            out.append(piece[:limit])
            piece=piece[limit:]
        if piece:
            out.append(piece)
    return out


def chunks(text:str,limit:int=CHUNK_CHARS):
    out,cur=[],""
    for block in re.split(r"\n\s*\n",text):
        block=block.strip()
        if not block:
            continue
        for i,unit in enumerate(_units(block,limit)):
            sep="\n\n" if i==0 else " "
            if cur and len(cur)+len(sep)+len(unit)>limit:
                out.append(cur)
                cur=unit
            else:
                cur=f"{cur}{sep}{unit}" if cur else unit
    if cur:
        out.append(cur)
    return out
