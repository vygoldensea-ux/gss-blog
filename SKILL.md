# GSS Blog Publisher — SKILL.md
# goldenseastudios.com | WordPress | Cowork + GitHub Actions

## MỤC TIÊU
Nhận keyword → research → viết bài chuẩn SEO → tạo ảnh → publish WordPress → báo cáo.
Không hỏi lại. Không xác nhận. Chỉ báo cáo sau khi xong.

---

## BƯỚC 0 — ĐỌC CONFIG TRƯỚC KHI LÀM BẤT CỨ ĐIỀU GÌ
- `config/categories.json` → slug category thật trong WP
- `config/tags.json` → slug tag thật trong WP

---

## CATEGORIES

| Topic | Slug |
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

KHÔNG dùng: ai-solutions, it-outsourcing, game-development, tech-news, tutorials, case-studies

---

## LOẠI BÀI

| Keyword | Loại |
|---|---|
| hướng dẫn, cách, how to | tutorial |
| so sánh, vs, nên chọn | comparison |
| phân tích, xu hướng, tại sao | insight |
| tin, mới nhất, ra mắt | news |
| dự án, case study, kết quả | case-study |
| Không rõ | insight |

---

## ĐỘ DÀI CHUẨN SEO

| Loại | Tối thiểu | Lý tưởng |
|---|---|---|
| tutorial | 1500 | 1800-2200 |
| comparison | 1400 | 1600-2000 |
| insight | 1600 | 2000-2500 |
| news | 600 | 700-900 |
| case-study | 1200 | 1500-1800 |

Bài dưới mức tối thiểu KHÔNG publish — viết thêm.

---

## PIPELINE

### Bước 1: Fetch bài đã publish
python main.py --fetch-posts
Dùng để tạo internal links.

### Bước 2: Research (BẮT BUỘC)
Dùng web_search tìm:
- Primary keyword: cụm từ chính, đặt trong H1 + 100 từ đầu + 2-3 H2
- LSI keywords: 5-8 từ liên quan, rải đều bài
- Top 3 competitor: xem họ viết gì, viết đầy đủ hơn
- Ít nhất 3 số liệu có nguồn (năm, %, tên tổ chức)
- Nguồn uy tín: Gartner, Statista, McKinsey, Forbes, GitHub

### Bước 3: Viết bài HTML
Theo cấu trúc loại bài bên dưới. Lưu vào output.html.

### Bước 4: Tự kiểm tra
- Đủ số từ theo loại bài
- H1 chứa primary keyword
- 100 từ đầu có primary keyword
- Ít nhất 3 stat có nguồn
- Có FAQ section (3+ câu)
- Có 2-3 internal links
- Có CTA block cuối bài
- Excerpt 120-155 ký tự có primary keyword

### Bước 5: Tạo output.meta và push GitHub
```
TITLE="..."
TYPE="tutorial"
CATEGORY="ai-agency"
TAGS="ai ai-trend"
SLUG="slug-ngan-5-tu"
EXCERPT="120-155 ky tu co primary keyword va ly do doc."
LANG="vi"
IMAGE_QUERIES="keyword anh 1|keyword anh 2"
PUBLISH="true"
```

```bash
cd ~/Desktop/gss-blog-v2
git add output.html output.meta
git commit -m "post: [slug]"
git push origin main
```

### Bước 6: Báo cáo
Title / URL / Số chữ / Category / Tags / Primary keyword / Số stat / FAQ / Internal links / Ảnh / Trạng thái

---

## CẤU TRÚC BÀI

### Tutorial (1500-2200 từ)
```
H1: Hướng dẫn [action] với [tool]: [kết quả cụ thể] — có primary keyword

[Mở đầu 150-200 từ: vấn đề + tại sao bài này giải quyết + primary keyword]

H2: [Tool] là gì? (LSI keyword)
  200 từ: định nghĩa, tính năng chính, so sánh ngắn alternatives

H2: Tại sao nên dùng [Tool]? (có stat)
  150 từ: 3-4 lý do + số liệu cụ thể
  <ul> bullet points

H2: Yêu cầu trước khi bắt đầu
  100 từ: checklist cần chuẩn bị

H2: Bước 1 — [Action] (LSI keyword)
  200-250 từ: hướng dẫn chi tiết
  H3: sub-step nếu cần
  <blockquote class="gss-tip"> tip quan trọng

H2: Bước 2 — [Action]
  200-250 từ

H2: Bước 3 — [Action]
  200-250 từ + code block nếu có

H2: Bước 4 — [Action]
  200 từ

H2: Lỗi thường gặp và cách fix
  200 từ: 3-5 lỗi + solution
  <ul> hoặc <ol>

H2: Câu hỏi thường gặp (FAQ) — BẮT BUỘC
  <h3>Câu hỏi 1?</h3><p>Trả lời 50-100 từ.</p>
  <h3>Câu hỏi 2?</h3><p>Trả lời...</p>
  <h3>Câu hỏi 3?</h3><p>Trả lời...</p>
  <h3>Câu hỏi 4?</h3><p>Trả lời...</p>

H2: Kết luận
  100-150 từ: tóm tắt + next steps + CTA block
```

### Insight (1600-2500 từ)
```
H1: [Power word] + [Primary Keyword] + [Năm] (50-65 ký tự)

[Mở đầu 150-200 từ: hook bằng stat + primary keyword + preview]

H2: Key Takeaways
  <ul> 4-5 bullet — người đọc quét qua biết ngay

H2: Bối cảnh — Tại sao quan trọng năm [năm]?
  200 từ + 1-2 stat có nguồn

H2: [Điểm chính 1] (LSI keyword) — có data
  300 từ + stat + ví dụ
  H3: sub-point nếu cần

H2: [Điểm chính 2] — có data
  300 từ

H2: [Điểm chính 3] — có data
  300 từ

H2: Thách thức và rủi ro
  200 từ — balanced view

H2: Ý nghĩa với [CTO / startup / business owner]
  200 từ — actionable insights

H2: Câu hỏi thường gặp (FAQ) — BẮT BUỘC
  3-4 Q&A

H2: Kết luận
  100-150 từ + CTA
```

### Comparison (1400-2000 từ)
```
H1: [A] vs [B]: Nên chọn cái nào cho [use case] [năm]?

[Mở đầu 100-150 từ + primary keyword]

H2: So sánh tổng quan (BẢNG HTML BẮT BUỘC)
  Bảng 5-7 tiêu chí: tính năng, giá, ease of use, support, scalability

H2: [Tiêu chí 1] — So sánh chi tiết
  200 từ + H3 cho từng option

H2: [Tiêu chí 2]
  200 từ

H2: [Tiêu chí 3]
  200 từ

H2: Chi phí thực tế
  200 từ + bảng giá + hidden costs

H2: Khi nào nên chọn [A]?
  150 từ + 3-4 use cases

H2: Khi nào nên chọn [B]?
  150 từ

H2: Câu hỏi thường gặp (FAQ) — BẮT BUỘC
  3-4 Q&A

H2: Kết luận + Recommendation
  100 từ + CTA
```

### News (600-900 từ)
```
H1: [What Happened]: [Key Detail] ([Năm])

[Mở đầu 100 từ: 5W1H]

H2: Chuyện gì đã xảy ra?
  150 từ — facts only

H2: Tại sao điều này quan trọng?
  150 từ + context + impact

H2: Phản ứng từ ngành
  100 từ

H2: Điều này thay đổi gì?
  150 từ

H2: Cần theo dõi điều gì tiếp theo?
  100 từ + CTA
```

### Case Study (1200-1800 từ)
```
H1: Cách [Project] [Đạt kết quả] với [Tech/Approach]

[Mở đầu 100-150 từ: kết quả ấn tượng trước]

H2: Bối cảnh và thách thức
  200 từ

H2: Mục tiêu đặt ra
  100 từ: KPIs cụ thể

H2: Giải pháp đề xuất
  200 từ: approach + tech stack + lý do chọn

H2: Quá trình triển khai
  250 từ
  H3: Phase 1
  H3: Phase 2

H2: Kết quả đạt được (SỐ LIỆU BẮT BUỘC)
  200 từ: trước vs sau, % improvement
  <ul> bullet points số liệu

H2: Bài học rút ra
  150 từ

H2: Câu hỏi thường gặp (FAQ) — BẮT BUỘC
  3 Q&A

H2: Dự án của bạn có tương tự không?
  100 từ + CTA mạnh
```

---

## SEO WRITING RULES

### Keyword placement BẮT BUỘC
- H1: primary keyword, 50-65 ký tự
- 100 từ đầu: primary keyword xuất hiện tự nhiên
- Ít nhất 3 H2 có LSI keyword
- Cuối bài: primary keyword 1 lần nữa
- Excerpt: có primary keyword, 120-155 ký tự
- Mật độ: 1-2%, không nhét

### Số liệu BẮT BUỘC
Ít nhất 3 stat/số liệu có nguồn mỗi bài.
Format: "Theo [Nguồn năm], X% doanh nghiệp..."
Nguồn: Gartner, Statista, McKinsey, Forbes, TechCrunch

### E-E-A-T signals
- Đề cập thực tế: "Trong các dự án chúng tôi triển khai..."
- Cite nguồn uy tín
- Internal link đến case studies/projects GSS

### FAQ — BẮT BUỘC (trừ news)
```html
<h2>Câu hỏi thường gặp</h2>
<h3>Câu hỏi 1?</h3>
<p>Trả lời 50-100 từ.</p>
<h3>Câu hỏi 2?</h3>
<p>Trả lời...</p>
```

---

## HTML RULES

```html
<!-- CTA — BẮT BUỘC mọi loại bài -->
<div class="gss-cta">
  <p><strong>Bạn cần đối tác triển khai?</strong></p>
  <p>We've helped 30+ startups ship AI, mobile &amp; game products from Vietnam.</p>
  <p><a href="https://goldenseastudios.com/contact-us/">Talk to Golden Sea Studios →</a></p>
</div>

<!-- Tip -->
<blockquote class="gss-tip">
  <strong>💡 Tip:</strong> Nội dung tip
</blockquote>

<!-- Ảnh — BẮT BUỘC có alt text chứa keyword -->
<figure>
  <img src="[url]" alt="[mô tả có primary keyword]" loading="lazy">
</figure>
```

Quy tắc:
- p tối đa 80 từ
- strong cho số liệu, tên tool, điểm quan trọng
- KHÔNG inline CSS
- KHÔNG dùng: game-changing, revolutionary, seamless, leverage, synergy, cutting-edge

---

## QUY TẮC VIẾT output.meta — BẮT BUỘC

Dùng dấu nháy KÉP, KHÔNG dùng nháy đơn trong value:

```
TITLE="IT Outsourcing in Vietnam 2026: What Is Changing"
TYPE="insight"
CATEGORY="it-solutions"
TAGS="it-solutions insight trend"
SLUG="it-outsourcing-vietnam-2026"
EXCERPT="Discover how Vietnam IT outsourcing market is evolving in 2026 with data on costs, talent, and trends."
LANG="en"
IMAGE_QUERIES="vietnam software developers office|it outsourcing team asia"
PUBLISH="true"
```

KHÔNG viết:
- TITLE='It's changing' ← dấu nháy đơn trong value gây lỗi shell
- EXCERPT="Vietnam's market" ← dấu nháy đơn gây lỗi

Thay apostrophe bằng cách viết khác:
- "It's" → "It is"
- "Vietnam's" → "Vietnam"
- "don't" → "do not"
