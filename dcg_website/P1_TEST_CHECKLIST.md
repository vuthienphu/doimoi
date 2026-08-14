# Checklist nghiệm thu P1 — Doimoi Website

## 1. Cài đặt và hồi quy

- [ ] Upgrade `dcg_website` thành công, không có ParseError/QWeb Error.
- [ ] `/`, `/solutions`, `/industries`, `/projects`, `/about`, `/contactus` trả HTTP 200.
- [ ] Header và Footer chỉ xuất hiện một lần trên mỗi trang.
- [ ] Desktop, tablet và mobile không có cuộn ngang hoặc vỡ lưới.

## 2. Dự án tiêu biểu

- [ ] Có menu **Quản lý Nội dung → Dự án tiêu biểu**.
- [ ] Editor tạo, sửa, xóa, sắp xếp và publish dự án được.
- [ ] Dự án nháp không xuất hiện ngoài website.
- [ ] Dự án publish xuất hiện trên `/projects` theo thứ tự.
- [ ] Chỉ dự án bật **Nổi bật trên trang chủ** xuất hiện ở trang chủ, tối đa 3 dự án.
- [ ] Ảnh dự án được resize tối đa 1200×800, hiển thị 16:9 và lazy-load.
- [ ] Không có ảnh thì placeholder hiển thị, không phát sinh ảnh 404.
- [ ] Link chi tiết chỉ xuất hiện khi Admin nhập URL.
- [ ] Thay đổi dự án được ghi trong Chatter.

## 3. Pagination và lazy loading

- [ ] Tạo ít nhất 7 ngành; `/industries` hiển thị 6 mục/trang và có pager.
- [ ] Tạo ít nhất 7 dự án; `/projects` hiển thị 6 mục/trang và có pager.
- [ ] Tạo ít nhất 13 dịch vụ; `/solutions` hiển thị 12 mục/trang và có pager.
- [ ] Chuyển trang không lặp hoặc bỏ sót bản ghi.
- [ ] Logo khách hàng, icon dịch vụ, ảnh ngành và ảnh dự án có `loading="lazy"`.
- [ ] Carousel khách hàng vẫn cuộn đúng sau thay đổi.

## 4. Resize ảnh

- [ ] Upload logo khách hàng lớn; dữ liệu lưu không vượt 512×512.
- [ ] Upload icon dịch vụ lớn; dữ liệu lưu không vượt 256×256.
- [ ] Upload ảnh ngành lớn; dữ liệu lưu không vượt 1600×900.
- [ ] Upload ảnh dự án lớn; dữ liệu lưu không vượt 1200×800.
- [ ] Ảnh không méo, không tràn card trên desktop/mobile.

## 5. Phân quyền và Record Rules

- [ ] Website Admin quản lý được toàn bộ nội dung CMS.
- [ ] Website Editor quản lý được Banner, Khách hàng, Dịch vụ, Ngành, Dự án và Nội dung trang.
- [ ] Website Editor chỉ đọc Nhóm dịch vụ theo ACL hiện có.
- [ ] Người không thuộc nhóm CMS không mở được các action quản trị.
- [ ] Visitor chỉ thấy nội dung publish do controller áp domain `is_published=True`.
- [ ] Record Rules của Editor không làm mất bản ghi nháp trong Backend.

## 6. Metadata SEO

- [ ] Mỗi Banner/CTA có tab **SEO**.
- [ ] Nhập SEO Title, Description, Keywords và ảnh chia sẻ rồi lưu.
- [ ] View Source có description, keywords, canonical, Open Graph và Twitter Card.
- [ ] `og:image` chỉ xuất hiện khi có ảnh SEO.
- [ ] Các trang không nhập SEO vẫn render bình thường và dùng title/subtitle banner làm fallback Open Graph.

## 7. Chống spam và CRM CTA

- [ ] Form có CSRF token và honeypot ẩn.
- [ ] Bot điền `website_check` bị từ chối, không tạo Lead.
- [ ] Gửi trong vòng dưới 2 giây sau khi mở form bị từ chối.
- [ ] Gửi lại trong vòng 60 giây cùng session bị rate-limit.
- [ ] Sau 60 giây có thể gửi yêu cầu hợp lệ tiếp theo.
- [ ] Form hợp lệ tạo đúng một CRM Lead với `request_type` chính xác.
- [ ] Thông báo thiếu trường và thông báo chống spam hiển thị khác nhau.

## 8. About và Contact từ Backend

- [ ] About: Sứ mệnh, giá trị, timeline và lãnh đạo chỉnh tại **Nội dung các trang**.
- [ ] Contact: tiêu đề thông tin, phản hồi và nội dung form chỉnh tại **Nội dung các trang**.
- [ ] Địa chỉ, điện thoại, email và website Contact lấy từ **Header & Footer**, không lấy `My Company`.
- [ ] Sửa dữ liệu Backend và refresh frontend thấy thay đổi, không cần sửa XML.

## 9. Ngoài phạm vi P1

- [ ] Xác nhận chưa triển khai P2: liên kết Contacts, newsletter, multi-website, snippet nâng cao và structured data nâng cao.
