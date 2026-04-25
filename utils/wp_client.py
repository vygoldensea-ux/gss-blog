"""
GSS Blog Publisher v2 — WordPress REST API Client
"""

import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _auth():
    user = os.getenv("WP_USERNAME", "")
    pwd  = os.getenv("WP_APP_PASSWORD", "")
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _site():
    return os.getenv("WP_SITE_URL", "").rstrip("/")


# ── POSTS ────────────────────────────────────────────────────

def fetch_published_posts(per_page=30):
    url = f"{_site()}/wp-json/wp/v2/posts"
    try:
        r = requests.get(url, params={"status": "publish", "per_page": per_page,
                                       "_fields": "id,title,link,slug"}, timeout=20)
        r.raise_for_status()
        posts = r.json()
        print(f"✅ Fetch {len(posts)} bài đã publish")
        return posts
    except Exception as e:
        print(f"⚠️  Fetch posts lỗi: {e}")
        return []


def format_posts_for_linking(posts):
    if not posts:
        return "Chưa có bài nào."
    lines = ["📋 BÀI ĐÃ PUBLISH:\n"]
    for p in posts:
        title = p.get("title", {}).get("rendered", "")
        link  = p.get("link", "")
        slug  = p.get("slug", "")
        lines.append(f"  • {title}")
        lines.append(f"    URL: {link}  |  slug: {slug}\n")
    return "\n".join(lines)


# ── TAXONOMY ─────────────────────────────────────────────────

def _get_term_id(taxonomy, slug):
    """Lấy ID của category hoặc tag từ slug"""
    url = f"{_site()}/wp-json/wp/v2/{taxonomy}"
    try:
        r = requests.get(url, params={"slug": slug, "per_page": 1, "hide_empty": False}, timeout=15)
        r.raise_for_status()
        items = r.json()
        if items:
            return items[0]["id"]
        print(f"❌ {taxonomy} slug '{slug}' không tồn tại trong WP!")
        return None
    except Exception as e:
        print(f"⚠️  Lấy {taxonomy} ID lỗi: {e}")
        return None


def _get_category_id(slug):
    cid = _get_term_id("categories", slug)
    if cid:
        print(f"✅ Category '{slug}' → ID {cid}")
    return cid


def _get_tag_ids(slugs):
    ids = []
    for s in slugs:
        tid = _get_term_id("tags", s)
        if tid:
            ids.append(tid)
            print(f"✅ Tag '{s}' → ID {tid}")
        else:
            print(f"⚠️  Tag '{s}' không tồn tại — bỏ qua")
    return ids


# ── MEDIA ────────────────────────────────────────────────────

def upload_image_to_wp(image_path, alt_text=""):
    url  = f"{_site()}/wp-json/wp/v2/media"
    hdrs = _auth()
    path = Path(image_path)

    ext_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".png": "image/png",  ".webp": "image/webp"}
    mime = ext_map.get(path.suffix.lower(), "image/jpeg")

    hdrs["Content-Disposition"] = f'attachment; filename="{path.name}"'
    hdrs["Content-Type"] = mime

    try:
        with open(path, "rb") as f:
            r = requests.post(url, headers=hdrs, data=f, timeout=60)
        r.raise_for_status()
        media = r.json()

        # Cập nhật alt text
        if alt_text:
            auth_h = _auth()
            auth_h["Content-Type"] = "application/json"
            requests.post(f"{_site()}/wp-json/wp/v2/media/{media['id']}",
                         headers=auth_h, json={"alt_text": alt_text}, timeout=15)

        print(f"✅ Upload ảnh: {media.get('source_url', '')}")
        return {"id": media["id"], "url": media["source_url"]}
    except Exception as e:
        print(f"❌ Upload ảnh lỗi: {e}")
        return None


# ── PUBLISH ──────────────────────────────────────────────────

def publish_post(
    title,
    html_content,
    category_slug,
    extra_category_slugs=None,
    tag_slugs=None,
    slug=None,
    excerpt=None,
    status="draft",
    featured_media_id=None,
):
    url  = f"{_site()}/wp-json/wp/v2/posts"
    hdrs = _auth()
    hdrs["Content-Type"] = "application/json"

    # Category IDs
    cat_id = _get_category_id(category_slug)
    if not cat_id:
        print(f"❌ Không tìm thấy category '{category_slug}' — hủy publish")
        return None

    cat_ids = [cat_id]
    for extra in (extra_category_slugs or []):
        eid = _get_category_id(extra)
        if eid and eid not in cat_ids:
            cat_ids.append(eid)

    tag_ids = _get_tag_ids(tag_slugs or [])

    payload = {
        "title":      title,
        "content":    html_content,
        "status":     status,
        "categories": cat_ids,
        "tags":       tag_ids,
    }
    if slug:
        payload["slug"] = slug
    if excerpt:
        payload["excerpt"] = excerpt
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    print(f"\n📤 Đang publish ({status.upper()})...")

    try:
        r = requests.post(url, headers=hdrs, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        body = ""
        if e.response is not None:
            try:
                body = e.response.json().get("message", e.response.text[:300])
            except Exception:
                body = e.response.text[:300]
        print(f"❌ Publish lỗi: {body}")
        return None
    except Exception as e:
        print(f"❌ Publish lỗi: {e}")
        return None
