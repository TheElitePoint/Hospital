"""Shared HTTP + page-text extraction. All external calls go through cache first."""
import re, html, requests
from .. import cache
from ..db import now

UA = "Mozilla/5.0 (compatible; TEP-HospitalResearch/0.1)"

def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s

def fetch_page(con, url, ttl_days=30, timeout=30):
    """Returns (text, status). Cached, so re-running a stage costs nothing."""
    hit = cache.get(con, "page", {"url": url}, ttl_days)
    if hit is not None:
        return hit.get("text", ""), hit.get("status", 200)
    try:
        r = session().get(url, timeout=timeout)
        text = extract_text(r.text) if r.ok else ""
        cache.put(con, "page", {"url": url}, {"text": text, "status": r.status_code},
                  ttl_days, r.status_code)
        return text, r.status_code
    except Exception as e:
        cache.put(con, "page", {"url": url}, {"text": "", "status": 0, "error": str(e)}, 1, 0)
        return "", 0

def extract_text(raw: str) -> str:
    """Strip markup to plain text. The citation validator matches excerpts against THIS,
    so it must stay stable - changing it invalidates cached verbatim checks."""
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw or "")
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()
