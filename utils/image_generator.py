"""
GSS Blog Publisher v2 — Image Generator
Cover : Pexels (reliable, no API issues)
Inline: Pexels + Unsplash
"""

import os, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_KEY   = os.getenv("PEXELS_API_KEY", "")

COVER_QUERIES = {
    "ai-agency":         "artificial intelligence technology blue",
    "it-solutions":      "software developers team office",
    "development":       "game development studio",
    "apps":              "mobile app smartphone",
    "digital-marketing": "digital marketing analytics",
    "seosmm":            "social media marketing",
    "ui-ux-design":      "UX design workspace",
    "identity":          "brand design creative",
    "modern-agency":     "modern tech team",
    "consultant-agency": "business consulting",
    "blog":              "technology abstract",
    "uncategorized":     "technology professional",
}

INLINE_QUERIES = {
    "ai-agency":    ["artificial intelligence", "machine learning"],
    "it-solutions": ["software development", "remote work"],
    "development":  ["game development", "3D design"],
    "apps":         ["mobile app", "smartphone"],
    "blog":         ["technology", "digital"],
}

def _pexels(query):
    if not PEXELS_KEY: return None
    try:
        r = requests.get("https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 1, "orientation": "landscape"}, timeout=10)
        hits = r.json().get("photos", [])
        if hits:
            return {"url": hits[0]["src"]["large2x"], "alt": hits[0].get("alt") or query}
    except: pass
    return None

def _unsplash(query):
    if not UNSPLASH_KEY: return None
    try:
        r = requests.get("https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}, timeout=10)
        hits = r.json().get("results", [])
        if hits:
            return {"url": hits[0]["urls"]["regular"], "alt": hits[0].get("alt_description") or query}
    except: pass
    return None

def _download_tmp(url, filename):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        path = f"/tmp/{filename}"
        open(path, "wb").write(r.content)
        return path
    except: return None

def generate_all_images(article_type, category, image_queries=None, cover_prompt=None):
    result = {"cover_path": None, "inline_images": []}
    
    # Cover
    q = cover_prompt or COVER_QUERIES.get(category, "technology professional")
    print(f"🎨 Cover từ Pexels: '{q}'...")
    img = _pexels(q) or _unsplash(q)
    if img:
        result["cover_path"] = _download_tmp(img["url"], "gss_cover.jpg")
        if result["cover_path"]: print(f"✅ Cover OK")
    
    # Inline
    queries = image_queries or INLINE_QUERIES.get(category, ["technology", "professional"])
    count = 1 if article_type == "news" else 2
    print(f"📸 Inline {count} ảnh...")
    images = []
    for q in queries[:2]:
        if len(images) >= count: break
        i = _pexels(q) or _unsplash(q)
        if i:
            images.append(i)
            print(f"✅ [{q}]")
        time.sleep(0.3)
    result["inline_images"] = images
    return result
