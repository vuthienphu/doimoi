# Checklist nghiệm thu P2 — Doimoi Website

## 1. Chuẩn bị và hồi quy

- [ ] Module `dcg_website` ở trạng thái Installed.
- [ ] Upgrade module không có ParseError, QWeb Error hoặc lỗi registry.
- [ ] `/`, `/solutions`, `/industries`, `/projects`, `/about`, `/contactus` trả HTTP 200.
- [ ] Header, Footer và CTA không bị lặp trên bất kỳ trang nào.
- [ ] Kiểm tra desktop, tablet và mobile; không có cuộn ngang.

## 2. Liên kết khách hàng với Contacts

- [ ] Form **Khách hàng tiêu biểu** có trường **Liên hệ / Công ty**.
- [ ] Chọn một Contact tự điền tên, website và logo nếu Contact có dữ liệu.
- [ ] Sau khi tự điền, Admin vẫn chỉnh riêng tên/logo hiển thị website được.
- [ ] Xóa Contact không xóa bản ghi Khách hàng; liên kết chuyển về trống.
- [ ] Khách hàng không liên kết Contact vẫn hoạt động như trước.
- [ ] Thay đổi liên kết được ghi trong Chatter.

## 3. Bản tin

- [ ] Xác nhận khối đăng ký bản tin không còn xuất hiện trên frontend theo phạm vi đã thống nhất.
- [ ] Module không còn phụ thuộc `mass_mailing` và không còn route/template newsletter không sử dụng.

## 4. Multi-website

- [ ] Các model Banner, Khách hàng, Dịch vụ, Số liệu, Ngành, Dự án và Nội dung trang có trường **Website**.
- [ ] Bản ghi để trống Website được coi là nội dung dùng chung.
- [ ] Bản ghi chọn Website A không xuất hiện trên Website B.
- [ ] Banner riêng của Website được ưu tiên hơn banner dùng chung cùng loại trang.
- [ ] Menu **Header & Footer** cho phép Website Admin tạo một cấu hình cho mỗi Website.
- [ ] Không thể tạo hai cấu hình Header & Footer cho cùng một Website.
- [ ] Header, Footer và Contact lấy đúng cấu hình của website hiện tại.
- [ ] Danh sách Footer chỉ lấy Dịch vụ/Ngành dùng chung hoặc thuộc website hiện tại.

## 5. Snippet tùy chỉnh nâng cao

- [ ] Mở Website Builder và thấy nhóm snippet **Đổi Mới**.
- [ ] Kéo được snippet **CTA Đổi Mới** vào một trang.
- [ ] Kéo được snippet **Điểm nổi bật** vào một trang.
- [ ] Chỉnh text, link và số liệu trực tiếp bằng Website Builder rồi lưu được.
- [ ] Snippet dùng đúng font, màu cam, container và responsive của website.
- [ ] Xóa snippet khỏi trang không ảnh hưởng CTA/banner động đang quản lý trong Backend.

## 6. Structured data và SEO nâng cao

- [ ] View Source mỗi trang chính có một script `application/ld+json`.
- [ ] JSON-LD hợp lệ, không chứa HTML entity làm hỏng JSON.
- [ ] Có schema `Organization` với tên, logo, URL, email, điện thoại, địa chỉ và social.
- [ ] Có schema `WebSite` và liên kết `publisher` tới Organization.
- [ ] `/projects` có thêm schema `ItemList` đúng số dự án trên trang hiện tại.
- [ ] Metadata SEO P1 vẫn có title, description, canonical, Open Graph và Twitter Card.
- [ ] Kiểm tra URL thật bằng Schema Markup Validator/Google Rich Results Test trước production.

## 7. Phân quyền và dữ liệu

- [ ] Website Admin tạo được cấu hình Header & Footer cho website mới.
- [ ] Website Editor chỉ sửa cấu hình hiện có, không tạo/xóa cấu hình toàn site.
- [ ] Visitor không có quyền Backend với Contacts, Email Marketing hoặc CMS.
- [ ] Controller frontend chỉ đọc nội dung publish thuộc website hiện tại hoặc dùng chung.
- [ ] Dữ liệu P0/P1 hiện có vẫn xuất hiện vì `website_id` để trống là dùng chung.
