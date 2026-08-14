# Checklist nghiệm thu P0 — Doimoi Website

## 1. Chuẩn bị

- [ ] Upgrade module `dcg_website` thành công, không có `ERROR`, `CRITICAL` hoặc `ParseError` trong log.
- [ ] Xóa cache asset hoặc tải lại trình duyệt bằng `Ctrl + F5`.
- [ ] Có ba tài khoản thử nghiệm: Website Admin, Content Editor và Visitor chưa đăng nhập.
- [ ] Kiểm tra trên desktop ≥ 1200 px, tablet 768–991 px và mobile ≤ 575 px.

## 2. Banner/Hero động

- [ ] Admin thấy menu **Website → Quản lý Nội dung → Banner trang chủ**.
- [ ] Admin tạo được banner với nhãn, tiêu đề, mô tả, ảnh, hai nút và liên kết.
- [ ] Banner mới mặc định chưa xuất bản.
- [ ] Banner chưa publish không xuất hiện trên trang chủ.
- [ ] Banner publish xuất hiện đúng nội dung và thứ tự.
- [ ] Cụm từ nhấn mạnh trong tiêu đề được tô màu cam.
- [ ] Ảnh upload hiển thị đúng tỷ lệ, không méo và không vượt khung.
- [ ] Khi bỏ ảnh, Hero hiển thị fallback dashboard mà không có ảnh lỗi.
- [ ] Nút chính và nút phụ mở đúng URL Admin đã nhập.
- [ ] Khi không có banner publish, toàn bộ Hero được ẩn.

## 3. Khách hàng tiêu biểu và carousel

- [ ] Khách hàng mới mặc định `Đã xuất bản = Tắt`.
- [ ] Khách hàng chưa publish không xuất hiện trên trang chủ.
- [ ] Khách hàng publish hiển thị theo đúng `sequence`.
- [ ] Logo upload được thu kích thước và hiển thị không méo.
- [ ] Không có logo thì hiển thị tên viết tắt; không có tên viết tắt thì lấy hai ký tự đầu.
- [ ] Có Website URL thì card mở URL trong tab mới.
- [ ] Desktop hiển thị 4 card trong một khung.
- [ ] Tablet hiển thị 2 card trong một khung.
- [ ] Mobile hiển thị 1 card trong một khung.
- [ ] Nút `‹` và `›` cuộn đúng một khung, không nhảy bố cục.
- [ ] Có thể xem khách hàng thứ 5 trở đi.
- [ ] Khi không có khách hàng publish, cả section nền xám khách hàng được ẩn.

## 4. Dịch vụ/Giải pháp

- [ ] Dịch vụ nháp có thể lưu khi đang hoàn thiện nội dung.
- [ ] Không thể publish nếu thiếu icon; thông báo lỗi dễ hiểu.
- [ ] Không thể publish nếu thiếu mô tả ngắn; thông báo lỗi dễ hiểu.
- [ ] Có đủ icon và mô tả thì publish thành công.
- [ ] Dịch vụ publish hiển thị đúng nhóm và đúng `sequence`.
- [ ] Dịch vụ unpublish biến mất khỏi trang chủ và `/solutions`.
- [ ] Nhóm không còn dịch vụ publish không tạo section/tab trống.
- [ ] Trang chủ hiển thị tối đa 4 dịch vụ mỗi nhóm và có nút **Xem tất cả**.
- [ ] Upgrade module không ghi đè nội dung dịch vụ Admin đã sửa.

## 5. Số liệu nổi bật và quy tắc section trống

- [ ] Chỉ số mới mặc định chưa publish.
- [ ] Chỉ số publish hiển thị theo `sequence`.
- [ ] Tối đa 4 chỉ số xuất hiện trên trang chủ.
- [ ] Chỉ số unpublish biến mất ngay sau khi tải lại trang.
- [ ] Khi không có chỉ số publish, toàn bộ dải số liệu nền xám được ẩn.
- [ ] Không còn thông báo “Đang cập nhật” hoặc khung placeholder cho section động rỗng.

## 6. CTA và CRM Lead

- [ ] Nút **Đăng ký khảo sát** đưa tới form Liên hệ và giữ `request_type=survey`.
- [ ] Nút **Trao đổi chuyên gia** đưa tới form và giữ `request_type=expert`.
- [ ] Nút **Đăng ký demo** trên Hero giữ `request_type=demo`.
- [ ] Gửi thiếu họ tên, công ty hoặc số điện thoại bị từ chối.
- [ ] Gửi đủ dữ liệu tạo đúng một CRM Lead.
- [ ] Lead chứa họ tên, công ty, điện thoại, email và mô tả.
- [ ] Mô tả Lead ghi đúng loại yêu cầu `survey`, `expert`, `demo` hoặc `consulting`.
- [ ] Sau khi gửi thành công, frontend hiển thị thông báo xác nhận.
- [ ] Form có CSRF token; POST không có token hợp lệ bị từ chối.

## 7. Chatter và lịch sử chỉnh sửa

- [ ] Form Banner có chatter.
- [ ] Form Khách hàng có chatter.
- [ ] Form Nhóm dịch vụ có chatter.
- [ ] Form Dịch vụ có chatter.
- [ ] Form Số liệu có chatter.
- [ ] Form Ngành có chatter.
- [ ] Đổi tên, mô tả, thứ tự hoặc trạng thái publish tạo dòng lịch sử.
- [ ] Upload ảnh hoạt động bình thường; ảnh không tạo tracking binary gây lỗi.

## 8. Phân quyền

- [ ] Website Admin tạo/sửa/xóa/publish Banner, Khách hàng, Dịch vụ, Nhóm dịch vụ và Số liệu.
- [ ] Website Admin sử dụng được Website Builder/Designer.
- [ ] Content Editor tạo/sửa/xóa/publish Banner, Khách hàng, Dịch vụ và Số liệu.
- [ ] Content Editor chỉ đọc Nhóm dịch vụ, không tạo/sửa/xóa danh mục nhóm.
- [ ] Content Editor không chỉnh được cấu trúc field hoặc quyền hệ thống.
- [ ] Visitor không truy cập được menu Backend quản trị nội dung.
- [ ] Visitor chỉ thấy bản ghi `is_published=True`.

## 9. Responsive và hồi quy

- [ ] `/`, `/solutions`, `/industries`, `/about`, `/contactus` đều trả HTTP 200.
- [ ] Header và Footer không bị vỡ trên desktop/tablet/mobile.
- [ ] Không có thanh cuộn ngang ngoài ý muốn.
- [ ] Không có lỗi JavaScript trong Console khi bấm carousel.
- [ ] Không có ảnh 404 hoặc template QWeb bị thiếu.
- [ ] Không có lỗi mới trong log Odoo sau khi duyệt toàn bộ năm trang.
