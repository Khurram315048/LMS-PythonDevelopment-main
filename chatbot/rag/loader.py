import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from .settings import DOCS_DIR,ROLES,EXTENSIONS



_META=re.compile(r"^---\s*\n(.*?)\n---\s*\n",re.S)
_HTML_META=re.compile(r"<!--\s*(title|link)\s*:\s*(.*?)\s*-->",re.I)


def _safe_link(v:str)->str:
    v=(v or "").strip()
    return v if v.startswith("/") or v.startswith("https://") else ""


def _parse_meta(raw:str):
    meta={}
    m=_META.match(raw)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k,_,v=line.partition(":")
                meta[k.strip().lower()]=v.strip()
        raw=raw[m.end():].strip()
    return meta,raw


@dataclass
class Document:
    key:str        
    source:str     
    role:str
    title:str
    pages:list  
    link:str=""   


class _HTMLText(HTMLParser):
    SKIP={"script","style","head","nav","footer"}
    HEAD={"h1":"# ","h2":"## ","h3":"## "}
    PARA={"p","div","section","article","ul","ol","table"}
    LINE={"li","br","tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out=[]
        self.skip=0

    def handle_starttag(self,tag,attrs):
        if tag in self.SKIP:
            self.skip+=1
            return
        if self.skip:
            return
        if tag in self.HEAD:
            self.out.append("\n\n"+self.HEAD[tag])
        elif tag in self.PARA:
            self.out.append("\n\n")
        elif tag in self.LINE:
            self.out.append("\n")

    def handle_endtag(self,tag):
        if tag in self.SKIP:
            self.skip=max(0,self.skip-1)
            return
        if not self.skip and tag in self.HEAD:
            self.out.append("\n\n")

    def handle_data(self,data):
        if not self.skip:
            self.out.append(data)


def _tidy(text:str)->str:
    lines=[re.sub(r"[ \t]+"," ",l).strip() for l in text.replace("\r","").split("\n")]
    return re.sub(r"\n{3,}","\n\n","\n".join(lines)).strip()


def _html_to_text(html:str)->str:
    html=re.sub(r"\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}","",html,flags=re.S)   # Jinja template tags
    p=_HTMLText()
    p.feed(html)
    return _tidy("".join(p.out))


def _read_pdf(path:Path):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("PDF ke liye: py -3.13 -m pip install pypdf")
    pages=[]
    for i,page in enumerate(PdfReader(str(path)).pages,1):
        text=(page.extract_text() or "").strip()
        if text:
            text=re.sub(r"(?<!\n)\n(?!\n)"," ",text)          
            pages.append((i,_tidy(text)))
    return pages


# def load_documents():
#     docs,skipped=[],[]
#     if not DOCS_DIR.exists():
#         return docs,[f"{DOCS_DIR} no folder found"]
#     for path in sorted(DOCS_DIR.rglob("*")):
#         if not path.is_file() or path.suffix.lower() not in EXTENSIONS or path.name.startswith(("_",".")):
#             continue
#         rel=path.relative_to(DOCS_DIR)
#         key=rel.as_posix()
#         folder_role=rel.parts[0] if len(rel.parts)>1 and rel.parts[0] in ROLES else None
#         header_role=None
#         try:
#             if path.suffix.lower()==".pdf":
#                 pages=_read_pdf(path)
#                 if not pages:
#                     skipped.append(f"{key}: no text found(scanned PDF? OCR want)")
#                     continue
#             else:
#                 raw=path.read_text(encoding="utf-8-sig",errors="replace").strip()
#                 if path.suffix.lower() in (".html",".htm"):
#                     raw=_html_to_text(raw)
#                 elif raw.lower().startswith("role:"):
#                     first,_,raw=raw.partition("\n")
#                     header_role=first.split(":",1)[1].strip().lower()
#                     raw=raw.strip()
#                 pages=[(None,raw)] if raw else []
#                 if not pages:
#                     skipped.append(f"{key}: empty file")
#                     continue
#         except Exception as e:
#             skipped.append(f"{key}: not readable ({e})")
#             continue
#         role=folder_role or header_role
#         if role not in ROLES:
#             skipped.append(f"{key}: No role found. File should be in docs/student, docs/teacher, docs/admin or docs/all  "
#                            f"(ya .md ki first line 'role: all')")
#             continue
#         docs.append(Document(key=key,source=path.stem,role=role,
#                              title=path.stem.replace("_"," ").replace("-"," ").title(),pages=pages))
#     return docs,skipped





def load_documents():
    docs,skipped=[],[]
    if not DOCS_DIR.exists():
        return docs,[f"{DOCS_DIR} no folder found"]
    for path in sorted(DOCS_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS or path.name.startswith(("_",".")):
            continue
        rel=path.relative_to(DOCS_DIR)
        key=rel.as_posix()
        folder_role=rel.parts[0] if len(rel.parts)>1 and rel.parts[0] in ROLES else None
        header_role=None
        meta={}
        try:
            if path.suffix.lower()==".pdf":
                pages=_read_pdf(path)
                if not pages:
                    skipped.append(f"{key}: no text found(scanned PDF? OCR want)")
                    continue
            else:
                raw=path.read_text(encoding="utf-8-sig",errors="replace").strip()
                if path.suffix.lower() in (".html",".htm"):
                    meta={k.lower():v for k,v in _HTML_META.findall(raw)}
                    raw=_html_to_text(raw)
                else:
                    meta,raw=_parse_meta(raw)
                    if raw.lower().startswith("role:"):
                        first,_,raw=raw.partition("\n")
                        header_role=first.split(":",1)[1].strip().lower()
                        raw=raw.strip()
                header_role=(meta.get("role") or header_role or "").lower() or None
                pages=[(None,raw)] if raw else []
                if not pages:
                    skipped.append(f"{key}: empty file")
                    continue
        except Exception as e:
            skipped.append(f"{key}: not readable ({e})")
            continue
        role=folder_role or header_role
        if role not in ROLES:
            skipped.append(f"{key}: No role found. File should be in docs/student, docs/teacher, docs/admin or docs/all  "
                           f"(ya .md ki first line 'role: all')")
            continue
        docs.append(Document(key=key,source=path.stem,role=role,
                             title=meta.get("title") or path.stem.replace("_"," ").replace("-"," ").title(),
                             link=_safe_link(meta.get("link")),
                             pages=pages))
    return docs,skipped