"""
GSS Blog Publisher v2 — Image Generator
Cover : Nano Banana via kie.ai (endpoint: /api/v1/jobs/createTask)
Inline: Unsplash → Pexels (fallback)
"""

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

KIE_KEY      = os.getenv("KIE_API_KEY", "")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_KEY   = os.getenv("PEXELS_API_KEY", "")

COVER_PROMPTS = {
    "ai-agency":         "Futuristic AI concept, glowing neural network nodes, deep blue and gold tones, professional tech art, 16:9, no text",
    "it-solutions":      "Modern software development team collaborating in bright office, diverse professionals, natural light, no text",
    "development":       "Game development studio, neon accent lighting, multiple monitors showing 3D environments, cinematic, no text",
    "apps":              "Mobile app development concept, smartphone interfaces, clean modern design, blue tones, no text",
    "digital-marketing": "Digital marketing dashboard with growth charts, vibrant modern office, no text",
    "seosmm":            "SEO and social media concept, graph trending up, connected network, clean professional, no text",
    "ui-ux-design":      "UI/UX design workspace, wireframes on screen, minimal clean desk, no text",
    "identity":          "Brand identity concept, logo design elements, creative studio, warm tones, no text",
    "modern-agency":     "Modern tech agency team, collaborative workspace, professional, no text",
    "consultant-agency": "Business consulting, professional meeting room, confident team, no text",
    "blog":              "Abstract technology background, clean minimal editorial style, blue white gradient, 16:9, no text",
    "uncategorized":     "Abstract technology background, clean minimal, blue white gradient, 16:9, no text",
}

INLINE_FALLBACKS = {
    "ai-agency":    ["artificial intelligence technology", "machine learning concept"],
    "it-solutions": ["software development team", "remote developers working"],
    "development":  ["game development workspace", "3D game design"],
    "apps":         ["mobile app design", "smartphone interface"],
    "blog":         ["technology concept", "digital innovation"],
}


# ── NANO BANANA (kie.ai) ─────────────────────────────────────

def _generate_cover_kie(prompt):
    if not KIE_KEY:
        print("⚠️  KIE_API_KEY chưa có")
        return None

    headers = {
        "Authorization": f"Bearer {KIE_KEY}",
        "Content-Type": "application/json"
    }

    # Đúng endpoint theo docs.kie.ai
    payload = {
        "model": "nano-banana",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "jpeg"
        }
    }

    try:
        r = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code != 200:
            print(f"⚠️  kie.ai {r.status_code}: {r.text[:200]}")
            return None

        data = r.json()
        task_id = (data.get("data", {}).get("taskId") or
                   data.get("taskId") or
                   data.get("task_id"))

        if not task_id:
            print(f"⚠️  kie.ai không trả về taskId: {str(data)[:200]}")
            return None

        print(f"   Task ID: {task_id} — đang poll...")
        return _poll_kie(task_id, headers)

    except Exception as e:
        print(f"⚠️  kie.ai lỗi: {e}")
        return None


def _poll_kie(task_id, headers, max_wait=120):
    """Poll task status theo docs.kie.ai"""
    for i in range(max_wait // 4):
        time.sleep(4)
        try:
            r = requests.get(
                f"https://api.kie.ai/api/v1/jobs/taskInfo/{task_id}",
                headers=headers,
                timeout=15
            )
            if r.status_code == 200:
                data   = r.json()
                d      = data.get("data", {})
                status = d.get("status", "")

                if status in ("completed", "success", "done", "finished", "COMPLETED", "SUCCESS"):
                    url = (d.get("output", {}).get("image_url") or
                           d.get("resultUrl") or
                           d.get("imageUrl") or
                           d.get("url"))
                    if url:
                        return _download_tmp(url, "gss_cover.jpg")
                    print(f"⚠️  Task done nhưng không có URL: {str(d)[:200]}")
                    return None

                elif status in ("failed", "error", "FAILED"):
                    print(f"⚠️  kie.ai task thất bại")
                    return None

                print(f"   [{i*4}s] status: {status}")
        except Exception as e:
            print(f"⚠️  Poll lỗi: {e}")

    print("⚠️  kie.ai timeout sau 2 phút")
    return None


def _download_tmp(url, filename):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        path = f"/tmp/{filename}"
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ Cover: {path}")
        return path
    except Exception as e:
        print(f"⚠️  Download lỗi: {e}")
        return None


# ── STOCK PHOTOS ─────────────────────────────────────────────

def _unsplash(query):
    if not UNSPLASH_KEY:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=10
        )
        hits = r.json().get("results", [])
        if hits:
            h = hits[0]
            return {"url": h["urls"]["regular"], "alt": h.get("alt_description") or query}
    except Exception:
        pass
    return None


def _pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=10
        )
        hits = r.json().get("photos", [])
        if hits:
            h = hits[0]
            return {"url": h["src"]["large"], "alt": h.get("alt") or query}
    except Exception:
        pass
    return None


def fetch_inline_images(queries, count=2):
    images = []
    for q in queries:
        if len(images) >= count:
            break
        img = _unsplash(q) or _pexels(q)
        if img:
            images.append(img)
            print(f"✅ Ảnh inline: '{q}'")
        time.sleep(0.3)
    return images


# ── MAIN ─────────────────────────────────────────────────────

def generate_all_images(article_type, category, image_queries=None, cover_prompt=None):
    result = {"cover_path": None, "inline_images": []}

    prompt = cover_prompt or COVER_PROMPTS.get(category, COVER_PROMPTS["blog"])
    print(f"🎨 Tạo cover (Nano Banana)...")
    print(f"   {prompt[:70]}...")
    result["cover_path"] = _generate_cover_kie(prompt)

    queries = image_queries or INLINE_FALLBACKS.get(category, ["technology professional"])
    count   = 1 if article_type == "news" else 2
    print(f"\n📸 Tìm {count} ảnh inline...")
    result["inline_images"] = fetch_inline_images(queries[:2], count=count)

    return result
