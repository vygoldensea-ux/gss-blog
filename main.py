"""
GSS Blog Publisher v2 — goldenseastudios.com
Clean rewrite, no conflicts.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from utils.wp_client import fetch_published_posts, format_posts_for_linking, publish_post, upload_image_to_wp
from utils.image_generator import generate_all_images
from utils.validators import validate_article, print_validation_report

VALID_CATEGORIES = {
    "ai-agency", "it-solutions", "development", "apps",
    "digital-marketing", "seosmm", "ui-ux-design",
    "identity", "modern-agency", "consultant-agency", "blog"
}

VALID_TYPES = {"insight", "tutorial", "comparison", "news", "case-study"}


def read_html(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File không tồn tại: {filepath}")
        sys.exit(1)
    content = path.read_text(encoding="utf-8")
    words = len(content.split())
    print(f"✅ Đọc file: {filepath} (~{words} từ)")
    return content


def fix_fonts(html, lang="en"):
    """Fix font cho WP"""
    if "font-family" in html[:500]:
        return html
    if lang == "vi":
        style = "<style>body,p,h1,h2,h3,h4,li,td,th{font-family:Arial,sans-serif}</style>"
    else:
        style = "<style>body,p,h1,h2,h3,h4,li,td,th{font-family:Arial,sans-serif}</style>"
    return style + html


def inject_cta(html, article_type):
    """Tự động thêm CTA nếu bài chưa có"""
    if "gss-cta" in html:
        return html
    if article_type not in ("insight", "comparison", "case-study"):
        return html

    contact_url = os.getenv("GSS_CONTACT_URL", "https://goldenseastudios.com/contact-us/")
    tagline = os.getenv("GSS_CTA_TAGLINE", "We've helped 30+ startups ship products from Vietnam")
    company = os.getenv("GSS_COMPANY_NAME", "Golden Sea Studios")

    cta = (
        '\n<div class="gss-cta" style="background:#f8f9fa;border-left:4px solid #c9a84c;padding:20px;margin:40px 0;">'
        '\n  <p><strong>Ready to build something great?</strong></p>'
        f'\n  <p>{tagline}.</p>'
        f'\n  <p><a href="{contact_url}">Talk to {company} →</a></p>'
        '\n</div>\n'
    )
    print(f"✅ Chèn CTA block")
    return html.rstrip() + cta


def insert_inline_images(html, images):
    """Chèn ảnh inline sau H2 thứ 2 và giữa bài"""
    import re
    positions = [m.start() for m in re.finditer(r"</h2>", html, re.IGNORECASE)]
    if not positions or not images:
        return html

    insert_at = []
    if len(positions) > 1:
        insert_at.append(positions[1])
    if len(positions) > 3:
        insert_at.append(positions[len(positions) // 2])

    offset = 0
    for pos, img in zip(insert_at, images):
        url = img.get("url") or img.get("wp_url", "")
        alt = img.get("alt", "")
        if not url:
            continue
        img_html = f'\n<figure><img src="{url}" alt="{alt}" loading="lazy"></figure>\n'
        actual = pos + len("</h2>") + offset
        html = html[:actual] + img_html + html[actual:]
        offset += len(img_html)

    return html


def main():
    parser = argparse.ArgumentParser(description="GSS Blog Publisher v2")

    parser.add_argument("--fetch-posts", action="store_true", help="Chỉ fetch danh sách bài đã publish")
    parser.add_argument("--file", help="File HTML bài viết")
    parser.add_argument("--title", help="Tiêu đề bài")
    parser.add_argument("--type", choices=list(VALID_TYPES), help="Loại bài")
    parser.add_argument("--category", help="Category slug (phải có trong categories.json)")
    parser.add_argument("--tags", nargs="+", default=[], help="Tag slugs")
    parser.add_argument("--slug", default=None, help="URL slug (tối đa 5 từ)")
    parser.add_argument("--excerpt", default=None, help="Meta description 120-155 ký tự")
    parser.add_argument("--image-queries", nargs="+", default=None, help="Keywords tìm ảnh inline")
    parser.add_argument("--cover-prompt", default=None, help="Custom prompt cho ảnh cover")
    parser.add_argument("--lang", choices=["en", "vi"], default="en", help="Ngôn ngữ bài viết")
    parser.add_argument("--publish", action="store_true", help="Publish ngay (mặc định: draft)")
    parser.add_argument("--skip-images", action="store_true", help="Bỏ qua tạo ảnh")
    parser.add_argument("--skip-validate", action="store_true", help="Bỏ qua validate")

    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  Golden Sea Studios — Blog Publisher v2")
    print("  goldenseastudios.com")
    print("=" * 55)

    # Mode: chỉ fetch posts
    if args.fetch_posts:
        print("\n📋 Fetch bài đã publish...")
        posts = fetch_published_posts()
        print(format_posts_for_linking(posts))
        return

    # Validate required args
    for arg, name in [(args.file, "--file"), (args.title, "--title"),
                      (args.type, "--type"), (args.category, "--category")]:
        if not arg:
            print(f"❌ Thiếu {name}")
            sys.exit(1)

    if args.category not in VALID_CATEGORIES:
        print(f"❌ Category '{args.category}' không hợp lệ!")
        print(f"   Dùng một trong: {', '.join(sorted(VALID_CATEGORIES))}")
        print(f"   Xem config/categories.json để biết thêm.")
        sys.exit(1)

    if not args.slug:
        print("⚠️  Không có --slug. WP tự generate — không tối ưu SEO.")

    status = "publish" if args.publish else "draft"

    # ── BƯỚC 1: ĐỌC FILE ──────────────────────────────────────
    html = read_html(args.file)

    # ── FIX FONTS ──────────────────────────────────────────────
    html = fix_fonts(html, lang=args.lang)
    print("✅ Font stack applied")

    # ── BƯỚC 2: VALIDATE ──────────────────────────────────────
    if not args.skip_validate:
        print("\n🔍 Kiểm tra chất lượng...")
        result = validate_article(html, args.title, args.type, args.slug, args.excerpt)
        print_validation_report(result)
        if not result["passed"]:
            answer = input("\n⚠️  Chưa đạt tiêu chuẩn. Vẫn tiếp tục? (y/N): ").strip().lower()
            if answer != "y":
                print("❌ Đã hủy.")
                sys.exit(0)
    else:
        print("⏭️  Bỏ qua validate")

    # ── BƯỚC 3: TẠO ẢNH ──────────────────────────────────────
    featured_media_id = None

    if not args.skip_images:
        print("\n🎨 Tạo ảnh...")
        img_result = generate_all_images(
            article_type=args.type,
            category=args.category,
            image_queries=args.image_queries,
            cover_prompt=args.cover_prompt
        )

        # Upload cover lên WP
        cover_path = img_result.get("cover_path")
        if cover_path:
            media = upload_image_to_wp(
                cover_path,
                alt_text=f"{args.title} — Golden Sea Studios"
            )
            if media:
                featured_media_id = media["id"]

        # Chèn inline vào HTML
        inline = img_result.get("inline_images", [])
        if inline:
            html = insert_inline_images(html, inline)
            print(f"✅ Chèn {len(inline)} ảnh inline")
    else:
        print("⏭️  Bỏ qua tạo ảnh")

    # ── BƯỚC 4: INJECT CTA ────────────────────────────────────
    html = inject_cta(html, args.type)

    # ── BƯỚC 5: PUBLISH ───────────────────────────────────────
    # Bài tiếng Việt → thêm category blog nếu chưa có
    extra_categories = []
    if args.lang == "vi" and args.category != "blog":
        extra_categories.append("blog")

    result = publish_post(
        title=args.title,
        html_content=html,
        category_slug=args.category,
        extra_category_slugs=extra_categories,
        tag_slugs=args.tags,
        slug=args.slug,
        excerpt=args.excerpt,
        status=status,
        featured_media_id=featured_media_id,
    )

    if result:
        post_url = result.get("link", "")
        print(f"\n{'=' * 55}")
        print(f"  ✅ HOÀN THÀNH")
        print(f"{'=' * 55}")
        print(f"  Title   : {args.title}")
        print(f"  URL     : {post_url}")
        print(f"  Status  : {status.upper()}")
        print(f"  Category: {args.category}")
        print(f"  Tags    : {', '.join(args.tags) if args.tags else 'none'}")
        print(f"  Lang    : {args.lang}")
        print(f"{'=' * 55}\n")
    else:
        print("\n❌ Publish thất bại.")
        sys.exit(1)


if __name__ == "__main__":
    main()
