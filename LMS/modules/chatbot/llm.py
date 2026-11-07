import asyncio
import logging
import httpx
from core.config import GROQ_API_KEY,GROQ_MODEL
try:
    from core.config import GROQ_FALLBACK_MODEL
except ImportError:
    GROQ_FALLBACK_MODEL=None

URL="https://api.groq.com/openai/v1/chat/completions"
_client=httpx.AsyncClient(timeout=25,limits=httpx.Limits(max_connections=100,max_keepalive_connections=20))


class ChatError(Exception):
    pass


async def call(payload:dict)->dict:
    if not GROQ_API_KEY:
        raise ChatError("Chatbot not configured")
    models=[GROQ_MODEL]+([GROQ_FALLBACK_MODEL] if GROQ_FALLBACK_MODEL else [])
    for model in models:
        payload={**payload,"model":model}
        for attempt in range(3):
            try:
                r=await _client.post(URL,json=payload,headers={"Authorization":f"Bearer {GROQ_API_KEY}"})
            except httpx.HTTPError:
                logging.exception("Groq request failed")
                await asyncio.sleep(0.5*2**attempt)
                continue
            if r.status_code==200:
                data=r.json()
                u=data.get("usage") or {}
                logging.info(f"LLM model={model} prompt={u.get('prompt_tokens')} completion={u.get('completion_tokens')}")
                return data
            if r.status_code in (429,500,502,503,504):
                try:
                    wait=min(float(r.headers.get("retry-after","")),5)
                except ValueError:
                    wait=0.5*2**attempt
                logging.warning(f"Groq {r.status_code} model={model} retry in {wait}s")
                await asyncio.sleep(wait)
                continue
            logging.error(f"Groq error {r.status_code}: {r.text[:300]}")
            break
    raise ChatError("Chatbot is busy. Please try again in a moment.")