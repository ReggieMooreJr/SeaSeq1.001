

Light Bible notes for the crawler.
"""
BOOK: SEA-SEC Scroll of Crawl

CHAPTER 1: Purpose
  V1  Walk pages starting from a URL.
  V2  Save basic facts: url, http status, size in bytes.
  V3  Keep it gentle so we don't hammer the site.

CHAPTER 2: Settings
  V1  MAX_PAGES = safety cap.
  V2  SAME_HOST_ONLY = stay on the same domain if True.
"""

import os
from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup

MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "50"))
SAME_HOST_ONLY = os.getenv("CRAWL_SAME_HOST_ONLY", "true").lower() == "true"

def normalize(u: str) -> str:
    # CHAPTER 3, V1: Remove #fragments; trim spaces; keep clean links.
    return urldefrag(u)[0].strip()

def crawl(start_url: str):
    """
    CHAPTER 4: The Walk
      V1  Use a queue to explore pages.
      V2  Record each page's status and size.
      V3  Add new links until we hit MAX_PAGES.
    """
    start_host = urlparse(start_url).netloc
    seen, out = set(), []
    q = deque([start_url])

    while q and len(out) < MAX_PAGES:
        url = q.popleft()
        if url in seen:
            continue
        seen.add(url)

        r = requests.get(url, timeout=20, headers={"User-Agent": "SEA-SEQ/1.0"})
        out.append({"url": url, "status": r.status_code, "bytes": len(r.content)})

        if "text/html" in r.headers.get("content-type", "") and r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            for a in soup.find_all("a", href=True):
                nxt = normalize(urljoin(url, a["href"]))
                if not nxt.startswith("http"):
                    continue
                if SAME_HOST_ONLY and urlparse(nxt).netloc != start_host:
                    continue
                if nxt not in seen:
                    q.append(nxt)
    return out
