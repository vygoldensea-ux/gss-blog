# GSS Blog Publisher — SKILL.md
# goldenseastudios.com | WordPress | Claude Code / Cowork

## MỤC TIÊU
Nhận keyword → research → viết bài → tạo ảnh → publish WordPress → báo cáo.
Không hỏi lại. Không xác nhận. Chỉ báo cáo sau khi xong.

---

## BƯỚC 0 — ĐỌC CONFIG TRƯỚC KHI LÀM BẤT CỨ ĐIỀU GÌ
Luôn đọc 2 file này trước:
- `config/categories.json` → slug category thật trong WP
- `config/tags.json` → slug tag thật trong WP

---

## CATEGORIES (dùng đúng slug trong categories.json)

| Topic | Slug dùng khi publish |
|---|---|
| AI, LLM, automation, ChatGPT, n8n | `ai-agency` |
| IT outsourcing, hire dev, offshore | `it-solutions` |
| Game dev, Unity, Unreal, mobile game | `development` |
| Mobile app, SaaS, product | `apps` |
| Marketing, growth hacking | `digital-marketing` |
| SEO, social media | `seosmm` |
| Design, UX/UI | `ui-ux-design` |
| Branding, identity | `identity` |
| Tin tức, tutorial, tổng hợp | `blog` |

**KHÔNG dùng:** `ai-solutions`, `it-outsourcing`, `game-development`, `tech-news`, `tutorials`, `case-studies` — những slug này KHÔNG tồn tại trong WP.

---

## LOẠI BÀI — tự detect từ keyword

| Keyword gợi ý | Loại |
|---|---|
| "hướng dẫn", "cách", "how to", "step by step" | `tutorial` |
| "so sánh", "vs", "nên chọn" | `comparison` |
| "phân tích", "xu hướng", "tại sao", "2025/2026" | `insight` |
| "tin", "mới nhất", "ra mắt", "update" | `news` |
| "dự án", "case study", "kết quả" | `case-study` |
| Không rõ → | `insight` |

---

## ĐỘ DÀI

| Loại | Từ |
|---|---|
| tutorial | 800–1500 |
| comparison | 800–1200 |
| insight | 1000–1800 |
| news | 400–700 |
| case-study | 800–1200 |

---

## PIPELINE — chạy tuần tự, không bỏ bước

### Bước 1: Fetch bài đã publish
```bash
python3 main.py --fetch-posts
```
Dùng kết quả để tạo internal links.

### Bước 2: Research
Dùng web_search tìm thông tin mới nhất về keyword. Ưu tiên nguồn < 6 tháng.

### Bước 3: Viết bài HTML
Cấu trúc theo loại bài (xem bên dưới). Ghi ra file `output.html`.

### Bước 4: Chạy publish
```bash
python3 main.py \
  --file output.html \
  --title "..." \
  --slug "..." \
  --type [insight|tutorial|comparison|news|case-study] \
  --category [slug-thật] \
  --tags [tag1] [tag2] \
  --excerpt "120-155 ký tự" \
  --image-queries "query1" "query2" \
  --lang [en|vi] \
  --publish
```

### Bước 5: Báo cáo
In ra: Title · URL · Số chữ · Category · Tags · Số ảnh · Trạng thái

---

## CẤU TRÚC BÀI THEO LOẠI

### Tutorial
```
H1: Hướng dẫn [action] với [tool] — [kết quả cụ thể]
H2: [Tool] là gì và tại sao nên dùng?
H2: Chuẩn bị trước khi bắt đầu
H2: Bước 1 — [action]
H2: Bước 2 — [action]
H2: Bước 3 — [action]
H2: Lỗi thường gặp
H2: Kết luận + CTA
```

### Insight
```
H1: [Power word] + [Keyword chính] + [Năm nếu cần]
H2: Tóm tắt nhanh
H2: Bối cảnh / Vì sao quan trọng
H2: [Điểm chính 1 — có data]
H2: [Điểm chính 2 — có data]
H2: [Điểm chính 3 — có data]
H2: Ý nghĩa với [độc giả mục tiêu]
H2: Kết luận + CTA
```

### Comparison
```
H1: [A] vs [B]: Nên chọn cái nào cho [use case]?
H2: So sánh nhanh (bảng HTML bắt buộc)
H2: [Tiêu chí 1]
H2: [Tiêu chí 2]
H2: Chi phí
H2: Khi nào chọn [A]
H2: Khi nào chọn [B]
H2: Kết luận + CTA
```

---

## HTML RULES

```html
<!-- CTA cuối bài — BẮT BUỘC với insight/comparison/case-study -->
<div class="gss-cta">
  <p><strong>Bạn cần đối tác triển khai hoặc tư vấn giải pháp?</strong></p>
  <p>We've helped 30+ startups ship AI, mobile &amp; game products from Vietnam.</p>
  <p><a href="https://goldenseastudios.com/contact-us/">Talk to Golden Sea Studios →</a></p>
</div>

<!-- Tip box -->
<blockquote class="gss-tip">
  <strong>💡 Tip:</strong> Nội dung tip quan trọng
</blockquote>

<!-- Bảng so sánh -->
<table>
  <thead><tr><th>Tiêu chí</th><th>A</th><th>B</th></tr></thead>
  <tbody><tr><td>...</td><td>...</td><td>...</td></tr></tbody>
</table>
```

Quy tắc:
- `<p>` tối đa 80 từ
- `<strong>` cho số liệu, tên tool, điểm quan trọng
- KHÔNG inline CSS
- KHÔNG dùng từ: "game-changing", "revolutionary", "seamless", "leverage", "synergy"

---

## SLUG RULES
- Tối đa 5 từ
- Chỉ a-z, 0-9, dấu gạch ngang
- Không dấu tiếng Việt
- Không stop words: the, a, an, and, or, for

---

## INTERNAL LINKS
- Chèn 2-3 internal links từ danh sách bài đã publish
- Link phải liên quan đến chủ đề bài
- Format: `<a href="https://goldenseastudios.com/[slug]/">[anchor text]</a>`

---

## NGÔN NGỮ
- `--lang en` → bài tiếng Anh (mặc định)
- `--lang vi` → bài tiếng Việt → tự động thêm category `blog` (nếu chưa có)

---

## STATUS MẶC ĐỊNH
- Mặc định: `draft`
- Dùng `--publish` khi user nói: "publish luôn", "đăng ngay", "không cần draft"

---

## PUBLISH VIA GITHUB ACTIONS

Thay vì chạy python3 main.py trực tiếp, Cowork sẽ push lên GitHub.
GitHub Actions tự chạy script và publish lên WordPress.

### Quy trình

```
1. Viết bài → lưu vào output.html
2. Tạo output.meta với đúng format
3. Git commit + push lên GitHub
4. GitHub Actions tự chạy trong ~2 phút
5. Bài lên web, có ảnh đầy đủ
```

### Format output.meta (BẮT BUỘC đúng format)

```bash
TITLE="Tiêu đề bài viết"
TYPE="tutorial"
CATEGORY="ai-agency"
TAGS="ai ai-trend business"
SLUG="slug-bai-viet"
EXCERPT="Mô tả 120-155 ký tự về bài viết này."
LANG="vi"
IMAGE_QUERIES="keyword ảnh 1|keyword ảnh 2"
PUBLISH="true"
```

### Git commands Cowork chạy

```bash
cd ~/Desktop/gss-blog-v2
git add output.html output.meta
git commit -m "post: [slug]"
git push origin main
```

### Xem kết quả

Sau khi push, vào:
`https://github.com/[username]/gss-blog/actions`
để xem tiến trình và báo cáo.
