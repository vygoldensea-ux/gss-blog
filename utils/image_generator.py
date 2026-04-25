"""
GSS Blog Publisher v2 — Image Generator
Cover : Nano Banana via kie.ai
Inline: Unsplash → Pexels → Pixabay (fallback)
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
PIXABAY_KEY  = os.getenv("PIXABAY_API_KEY", "")

COVER_PROMPTS = {
    "ai-agency":         "Futuristic AI concept, glowing neural network nodes, deep blue and gold tones, professional tech art, 16:9, no text",
    "it-solutions":      "Modern software development team collaborating in bright office, Vietnam tech hub, diverse professionals, natural light, no text",
    "development":       "Game development studio, neon accent lighting, multiple monitors showing 3D game environments, cinematic, no text",
    "apps":              "Mobile app development concept, smartphone interfaces floating, clean modern design, blue tones, no text",
    "digital-marketing": "Digital marketing dashboard with growth charts, laptop and analytics, vibrant modern office, no text",
    "seosmm":            "SEO and social media concept, graph trending up, connected network nodes, clean professional, no text",
    "ui-ux-design":      "UI/UX design workspace, wireframes and prototypes on screen, minimal clean desk, no text",
    "identity":          "Brand identity concept, logo design elements, creative studio aesthetic, warm tones, no text",
    "modern-agency":     "Modern tech agency team, collaborative workspace, Ho Chi Minh City backdrop, professional, no text",
    "consultant-agency": "Business consulting concept, professional meeting room, data on screens, confident team, no text",
    "blog":              "Abstract technology background, clean minimal editorial style, blue white gradient, 16:9, no text",
}

INLINE_FALLBACKS = {
    "ai-agency":         ["artificial intelligence technology", "machine learning concept"],
    "it-solutions":      ["software development team", "remote developers working"],
    "development":       ["game development workspace", "3D game design"],
    "apps":              ["mobile app design", "smartphone app interface"],
    "digital-marketing": ["digital marketing analytics", "social media growth"],
    "seosmm":            ["SEO optimization concept", "social media marketing"],
    "ui-ux-design":      ["UX design wireframe", "UI design prototype"],
    "identity":          ["brand identity design", "logo design creative"],
    "modern-agency":     ["modern tech team Vietnam", "creative agency workspace"],
    "consultant-agency": ["business consulting meeting", "strategy planning"],
    "blog":              ["technology concept", "digital innovation"],
}


# ── NANO BANANA (kie.ai) ─────────────────────────────────────

def _generate_cover_kie(prompt):
    """Tạo ảnh cover bằng Nano Banana (kie.ai)"""
    if not KIE_KEY:
        print("⚠️  KIE_API_KEY chưa có")
        return None

    headers = {
        "Authorization": f"Bearer {KIE_KEY}",
        "Content-Type": "application/json"
    }

    # Thử endpoint generate trực tiếp
    try:
        r = requests.post(
            "https://api.kie.ai/v1/images/generations",
            headers=headers,
            json={"prompt": prompt, "model": "nano-banana", "n": 1, "size": "1792x1024"},
            timeout=60
        )

        if r.status_code == 200:
            data = r.json()
            # Xử lý các format response khác nhau
            image_url = None
            if "data" in data and data["data"]:
                item = data["data"][0]
                image_url = item.get("url") or item.get("image_url")
                task_id   = item.get("task_id")
            else:
                image_url = data.get("url") or data.get("image_url")
                task_id   = data.get("task_id")

            if image_url:
                return _download_to_tmp(image_url, "gss_cover.png")

            if task_id:
                return _poll_kie_task(task_id, headers)

        print(f"⚠️  kie.ai trả {r.status_code}: {r.text[:200]}")
        return None

    except Exception as e:
        print(f"⚠️  kie.ai lỗi: {e}")
        return None


def _poll_kie_task(task_id, headers, max_wait=90):
    """Poll kie.ai task cho đến khi xong"""
    print(f"   Đợi kie.ai xử lý (task: {task_id})...")
    for _ in range(max_wait // 3):
        time.sleep(3)
        try:
            r = requests.get(
                f"https://api.kie.ai/api/v1/images/generations/{task_id}",
                headers=headers, timeout=15
            )
            if r.status_code == 200:
                data   = r.json()
                status = (data.get("status") or
                          data.get("data", {}).get("status", ""))
                if status in ("completed", "success", "done", "finished"):
                    url = (data.get("data", {}).get("images", [{}])[0].get("url")
                           or data.get("url"))
                    if url:
                        return _download_to_tmp(url, "gss_cover.png")
                elif status in ("failed", "error"):
                    print("⚠️  kie.ai task thất bại")
                    return None
        except Exception:
            pass
    print("⚠️  kie.ai timeout")
    return None


def _download_to_tmp(url, filename):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        path = f"/tmp/{filename}"
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ Cover đã lưu: {path}")
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
            return {"url": h["urls"]["regular"], "alt": h.get("alt_description") or query, "source": "unsplash"}
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
            return {"url": h["src"]["large"], "alt": h.get("alt") or query, "source": "pexels"}
    except Exception:
        pass
    return None


def _pixabay(query):
    if not PIXABAY_KEY:
        return None
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": PIXABAY_KEY, "q": query, "per_page": 3,
                    "image_type": "photo", "orientation": "horizontal", "safesearch": "true"},
            timeout=10
        )
        hits = r.json().get("hits", [])
        if hits:
            return {"url": hits[0]["webformatURL"], "alt": query, "source": "pixabay"}
    except Exception:
        pass
    return None


def fetch_inline_images(queries, count=2):
    images = []
    for q in queries:
        if len(images) >= count:
            break
        img = _unsplash(q) or _pexels(q) or _pixabay(q)
        if img:
            images.append(img)
            print(f"✅ Ảnh [{img['source']}]: '{q}'")
        else:
            print(f"⚠️  Không tìm được ảnh: '{q}'")
        time.sleep(0.3)
    return images


# ── MAIN PIPELINE ─────────────────────────────────────────────

def generate_all_images(article_type, category, image_queries=None, cover_prompt=None):
    result = {"cover_path": None, "inline_images": []}

    # Cover
    prompt = cover_prompt or COVER_PROMPTS.get(category, COVER_PROMPTS["blog"])
    print(f"🎨 Tạo cover (Nano Banana)...")
    print(f"   {prompt[:70]}...")
    result["cover_path"] = _generate_cover_kie(prompt)

    # Inline
    queries = image_queries or INLINE_FALLBACKS.get(category, ["technology professional"])
    count   = 1 if article_type == "news" else 2
    print(f"\n📸 Tìm {count} ảnh inline (Unsplash/Pexels)...")
    result["inline_images"] = fetch_inline_images(queries[:2], count=count)

    return result
