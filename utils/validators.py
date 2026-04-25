"""GSS Blog Publisher v2 — Content Validator"""
import re

BANNED = [
    "game-changing", "revolutionary", "cutting-edge", "leverage",
    "synergy", "seamless", "robust", "in today's fast-paced world",
    "it goes without saying", "deep dive", "scalable solution",
    "world-class", "best-in-class", "state-of-the-art",
]

REQUIREMENTS = {
    "insight":    {"min": 900,  "max": 2000, "h2": 4, "cta": True,  "table": False},
    "tutorial":   {"min": 700,  "max": 2000, "h2": 4, "cta": False, "table": False},
    "comparison": {"min": 700,  "max": 1500, "h2": 5, "cta": True,  "table": True},
    "news":       {"min": 350,  "max": 800,  "h2": 3, "cta": False, "table": False},
    "case-study": {"min": 700,  "max": 1500, "h2": 4, "cta": True,  "table": False},
}


def validate_article(html, title, article_type, slug=None, excerpt=None):
    errors, warnings = [], []
    req = REQUIREMENTS.get(article_type, REQUIREMENTS["insight"])

    text       = re.sub(r"<[^>]+>", " ", html)
    words      = len(text.split())
    h2_count   = len(re.findall(r"<h2", html, re.I))
    has_table  = bool(re.search(r"<table", html, re.I))
    has_cta    = "gss-cta" in html or "contact-us" in html or "contact us" in html.lower()

    if words < req["min"]:
        errors.append(f"Bài quá ngắn: {words} từ (tối thiểu {req['min']})")
    elif words > req["max"]:
        warnings.append(f"Bài hơi dài: {words} từ (tối đa {req['max']})")

    if h2_count < req["h2"]:
        errors.append(f"Cần ít nhất {req['h2']} H2, hiện có {h2_count}")

    if req["table"] and not has_table:
        errors.append("Bài comparison bắt buộc có bảng <table>")

    if req["cta"] and not has_cta:
        warnings.append("Nên có CTA block cuối bài")

    for phrase in BANNED:
        if phrase.lower() in text.lower():
            warnings.append(f"Cụm từ bị cấm: '{phrase}'")

    if excerpt and not (120 <= len(excerpt) <= 155):
        warnings.append(f"Excerpt {len(excerpt)} ký tự — cần 120-155")

    if not excerpt:
        warnings.append("Thiếu excerpt (meta description)")

    if title and len(title) > 70:
        warnings.append(f"Title dài {len(title)} ký tự — nên dưới 65")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {"words": words, "h2": h2_count, "has_table": has_table, "has_cta": has_cta}
    }


def print_validation_report(r):
    s = r["stats"]
    print(f"\n{'─'*45}")
    print(f"  QUALITY CHECK")
    print(f"{'─'*45}")
    print(f"  Từ      : {s['words']:,}")
    print(f"  H2      : {s['h2']}")
    print(f"  Bảng    : {'✅' if s['has_table'] else '—'}")
    print(f"  CTA     : {'✅' if s['has_cta'] else '⚠️'}")
    if r["errors"]:
        print(f"\n  ❌ ERRORS:")
        for e in r["errors"]:
            print(f"     • {e}")
    if r["warnings"]:
        print(f"\n  ⚠️  WARNINGS:")
        for w in r["warnings"]:
            print(f"     • {w}")
    print(f"\n  {'✅ ĐẠT' if r['passed'] else '❌ CHƯA ĐẠT'}")
    print(f"{'─'*45}")
