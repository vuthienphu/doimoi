# Quy trình kiểm thử `dcg_project_customize`

Tài liệu này dùng để kiểm thử module `dcg_project_customize` sau khi cài đặt hoặc nâng cấp trên Odoo 19.

## 1. Điều kiện trước khi kiểm thử

- Odoo đang chạy, ví dụ `http://localhost:8070`.
- Cơ sở dữ liệu đã cài các module phụ thuộc: `project`, `crm`, `mail`.
- Module `dcg_project_customize` đã được cài đặt hoặc nâng cấp.
- Người dùng kiểm thử có quyền người dùng Dự án hoặc quản lý Dự án.
- Các người dùng dùng để kiểm thử email có khai báo địa chỉ hợp lệ.
- Tham số `web.base.url` đã đúng với URL đang truy cập Odoo.

## 2. Nâng cấp module trước khi kiểm thử

Thao tác trên giao diện:

1. Vào `Ứng dụng`.
2. Tìm `DCG Project Customize`.
3. Bấm `Nâng cấp`.
4. Tải lại trình duyệt bằng `Ctrl + F5`.

Lệnh dòng lệnh tham khảo:

```powershell
E:\DM-Group\doimoi-master\.venv\Scripts\python.exe E:\DM-Group\odoo19\odoo-bin server -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_customize --http-port=8070
```

## 3. Luồng quay video demo

Luồng này nên quay theo thứ tự từ cấu hình đến nghiệp vụ để người xem hiểu được module làm gì.

### Phần 1: Giới thiệu module

1. Mở màn hình `Ứng dụng`.
2. Tìm `DCG Project Customize`.
3. Nói ngắn gọn: module tự động tạo Dự án từ Cơ hội đã thắng, bổ sung người kiểm tra, danh sách checklist, trạng thái giai đoạn công việc và email nhắc việc.

### Phần 2: Kiểm tra quy trình giai đoạn công việc

Đường dẫn:

```text
Dự án > Cấu hình > Giai đoạn công việc
```

1. Kiểm tra đã có các giai đoạn `Cần làm`, `Đang thực hiện`, `Chờ kiểm tra`, `Hoàn thành`, `Đã đưa lên Live`.
2. Mở giai đoạn `Đang thực hiện`, kiểm tra chỉ có cờ `Đang thực hiện`.
3. Mở giai đoạn `Chờ kiểm tra`, kiểm tra chỉ có cờ `Chờ kiểm tra`.
4. Mở giai đoạn `Hoàn thành`, kiểm tra chỉ có cờ `Hoàn thành`.
5. Mở giai đoạn `Đã đưa lên Live`, kiểm tra chỉ có cờ `Đã đưa lên Live`.

Điểm cần nói trong video:

- Module tạo sẵn quy trình Stage theo đặc tả, người dùng không phải nhập lại Stage mỗi lần tạo Task.
- Các cờ trạng thái này giúp hệ thống biết khi nào cần gửi email thông báo.
- Giai đoạn `Hoàn thành` nhưng chưa `Đã đưa lên Live` sẽ được cron nhắc việc hằng ngày.
- Mỗi giai đoạn nghiệp vụ chỉ chọn một cờ chính.
- Giai đoạn phải thuộc đúng Dự án của Công việc đang kiểm thử, hoặc là giai đoạn dùng chung không gán Dự án cụ thể.
- Không cần chọn `Mẫu email` của Odoo; module tự chọn mẫu email theo cờ trạng thái.

### Phần 3: Tạo Dự án từ Cơ hội đã thắng

Đường dẫn:

```text
CRM > Bán hàng > Quy trình bán hàng
```

1. Tạo một Cơ hội mới.
2. Nhập tên Cơ hội, Khách hàng và Nhân viên kinh doanh.
3. Bấm `Đã thắng` hoặc kéo Cơ hội sang giai đoạn đã thắng.
4. Bấm smart button `Dự án` trên Cơ hội.
5. Kiểm tra màn hình Công việc của Dự án vừa được mở.
6. Nếu cần kiểm tra form Dự án, mở Dự án từ app `Dự án` và kiểm tra:
   - Tên Dự án giống tên Cơ hội.
   - Khách hàng lấy từ Cơ hội.
   - Quản lý Dự án hoặc Nhân viên kinh doanh lấy từ Cơ hội.
   - Trường `Cơ hội` liên kết ngược về Cơ hội.

Điểm cần nói trong video:

- Khi Cơ hội đạt trạng thái đã thắng, hệ thống tự tạo Dự án.
- Nếu Cơ hội đã có Dự án liên kết thì hệ thống không tạo trùng.
- Smart button `Dự án` mở sang màn hình Công việc của Project trong app Dự án.

### Phần 4: Kiểm tra thông tin bổ sung trên công việc

Đường dẫn:

```text
Dự án > Dự án > [Dự án] > Công việc
```

1. Mở Dự án vừa tạo.
2. Tạo một Công việc mới.
3. Gán người thực hiện ở trường người được giao.
4. Gán người kiểm tra ở trường `Danh sách người kiểm tra`.
5. Nhập `Thời gian dự kiến hoàn thành`.
6. Nhập `Thời gian thực tế hoàn thành`.
7. Mở tab `Checklist`.
8. Thêm một vài dòng kiểm tra.
9. Chọn hoàn thành một dòng kiểm tra và lưu Công việc.

Điểm cần nói trong video:

- Công việc có thêm danh sách người kiểm tra để phục vụ bước kiểm tra.
- Danh sách checklist giúp theo dõi các hạng mục cần hoàn thành trong Công việc.
- Thời gian dự kiến và thời gian thực tế giúp theo dõi tiến độ.

### Phần 5: Demo email khi đổi giai đoạn công việc

1. Chuyển Công việc sang giai đoạn `Đang thực hiện`.
2. Kiểm tra email hoặc hàng đợi email.
3. Chuyển Công việc sang giai đoạn `Chờ kiểm tra`.
4. Kiểm tra email gửi cho người kiểm tra.
5. Chuyển Công việc sang giai đoạn `Hoàn thành`.
6. Kiểm tra email gửi cho người tạo Công việc và người được giao.

Điểm cần nói trong video:

- Mỗi trạng thái nghiệp vụ sử dụng một mẫu email riêng.
- Hệ thống chỉ gửi cho người dùng có email hợp lệ.
- Email có liên kết mở trực tiếp Công việc.

### Phần 6: Demo cron nhắc việc hằng ngày

Đường dẫn ở chế độ nhà phát triển:

```text
Cài đặt > Kỹ thuật > Tự động hóa > Tác vụ đã lên lịch
```

1. Mở cron `Nhắc việc hàng ngày`.
2. Bấm `Chạy thủ công`.
3. Kiểm tra email hoặc hàng đợi email.
4. Giải thích 3 nhóm nhắc việc:
   - Công việc đang thực hiện.
   - Công việc chờ kiểm tra.
   - Công việc đã hoàn thành nhưng chưa lên Live.

Điểm cần nói trong video:

- Cron chạy mỗi ngày.
- Nếu máy chủ dùng UTC thì `01:00:00` tương ứng 08:00 giờ Việt Nam.

### Phần 7: Kết luận video

Nói ngắn gọn:

- Module giúp chuyển đổi Cơ hội đã thắng thành Dự án tự động.
- Công việc có thêm danh sách người kiểm tra, danh sách checklist và thời gian hoàn thành.
- Giai đoạn công việc có cờ nghiệp vụ để điều khiển email.
- Cron tự động nhắc việc hằng ngày theo trạng thái Công việc.

## 4. Kiểm thử tạo Dự án từ Cơ hội

Đường dẫn:

```text
CRM > Bán hàng > Quy trình bán hàng
```

Trường hợp kiểm thử TC-PROJ-001: Tạo Dự án khi Cơ hội đã thắng

Bước thực hiện:

1. Tạo Cơ hội mới có Khách hàng và Nhân viên kinh doanh.
2. Đảm bảo Cơ hội chưa có Dự án liên kết.
3. Bấm `Đã thắng` hoặc kéo sang giai đoạn đã thắng.
4. Mở Dự án vừa tạo.

Kết quả mong đợi:

- Dự án được tạo tự động.
- Tên Dự án bằng tên Cơ hội.
- Khách hàng của Dự án lấy từ Khách hàng của Cơ hội.
- Người phụ trách Dự án lấy từ Nhân viên kinh doanh của Cơ hội.
- Dự án có liên kết ngược về Cơ hội.
- Nếu Cơ hội có trường `project_id`, trường này được gán Dự án vừa tạo.

Trường hợp kiểm thử TC-PROJ-002: Không tạo trùng Dự án khi chuyển lại trạng thái đã thắng

Bước thực hiện:

1. Dùng Cơ hội đã có Dự án.
2. Chuyển Cơ hội ra khỏi giai đoạn đã thắng.
3. Chuyển lại trạng thái đã thắng.
4. Kiểm tra danh sách Dự án.

Kết quả mong đợi:

- Không có Dự án trùng tên hoặc bị tạo lặp cho Cơ hội đó.
- Dự án cũ vẫn giữ `lead_id`.

Trường hợp kiểm thử TC-PROJ-003: Cơ hội đã có Dự án từ module khác

Bước thực hiện:

1. Dùng cơ sở dữ liệu có module tạo trường `crm.lead.project_id`.
2. Gán sẵn một Dự án vào Cơ hội.
3. Chuyển Cơ hội sang trạng thái đã thắng.
4. Mở Dự án đã gán sẵn.

Kết quả mong đợi:

- Hệ thống không tạo Dự án mới.
- Dự án đã gán sẵn có `lead_id = Cơ hội`.
- Cơ hội vẫn trỏ tới Dự án cũ.

## 5. Kiểm thử gán giai đoạn mặc định cho Dự án mới

Đường dẫn:

```text
Dự án > Cấu hình > Giai đoạn công việc
```

Trường hợp kiểm thử TC-PROJ-004: Gán giai đoạn mặc định cho Dự án

Bước thực hiện:

1. Nâng cấp module `dcg_project_customize`.
2. Tạo Dự án mới.
3. Mở kanban Công việc của Dự án mới.

Kết quả mong đợi:

- Dự án mới có đủ 5 giai đoạn mặc định: `Cần làm`, `Đang thực hiện`, `Chờ kiểm tra`, `Hoàn thành`, `Đã đưa lên Live`.
- Người dùng có thể tạo Công việc ngay, không cần nhập lại Stage.

## 6. Kiểm thử cấu hình giai đoạn công việc

Trường hợp kiểm thử TC-PROJ-005: Cờ trạng thái đã được cấu hình sẵn trên giai đoạn

Bước thực hiện:

1. Mở giai đoạn `Đang thực hiện`.
2. Mở giai đoạn `Chờ kiểm tra`.
3. Mở giai đoạn `Hoàn thành`.
4. Mở giai đoạn `Đã đưa lên Live`.

Kết quả mong đợi:

- Các cờ trạng thái hiển thị trên biểu mẫu giai đoạn.
- Mỗi giai đoạn đã được tick đúng cờ theo tên giai đoạn.
- Không cần chọn `Mẫu email` của Odoo.

## 7. Kiểm thử trường bổ sung trên Công việc

Đường dẫn:

```text
Dự án > Dự án > [Dự án] > Công việc
```

Trường hợp kiểm thử TC-PROJ-006: Hiển thị trường danh sách người kiểm tra và thời gian hoàn thành

Bước thực hiện:

1. Mở một Công việc.
2. Gán `Danh sách người kiểm tra`.
3. Nhập `Thời gian dự kiến hoàn thành`.
4. Nhập `Thời gian thực tế hoàn thành`.
5. Lưu Công việc.

Kết quả mong đợi:

- Các trường hiển thị trên biểu mẫu Công việc.
- Có thể chọn nhiều người kiểm tra.
- Hai trường ngày giờ lưu được.

Trường hợp kiểm thử TC-PROJ-007: Checklist trên Công việc

Bước thực hiện:

1. Mở tab `Checklist`.
2. Thêm 2 dòng kiểm tra.
3. Chọn `Đã hoàn thành` cho một dòng.
4. Lưu Công việc.
5. Mở lại Công việc.

Kết quả mong đợi:

- Checklist lưu được.
- Trạng thái `Đã hoàn thành` của từng dòng được giữ lại.
- Xóa Công việc thì các dòng kiểm tra con bị xóa theo.

## 8. Setup gửi email thật

Mục tiêu:

- Odoo gửi email thật ra Gmail hoặc tài khoản email bên ngoài.
- Email gửi đi dùng đúng `Email gửi thông báo` đã cấu hình trong module.

### 8.1. Cấu hình email gửi của module

Đường dẫn:

```text
Cài đặt > Project > Email thông báo DCG
```

Bước thực hiện:

1. Nhập `Email gửi thông báo`, ví dụ `company@gmail.com`.
2. Nhập `Tên người gửi`, ví dụ `DCG Project`.
3. Bấm `Lưu`.

Kết quả mong đợi:

- Cấu hình được lưu.
- Các email của module có người gửi theo dạng `DCG Project <company@gmail.com>`.

Lưu ý:

- Email này nên trùng với tài khoản SMTP dùng để gửi thật.
- Nếu bỏ trống, module tự dùng email công ty, nếu công ty chưa có email thì dùng email user hiện tại.

### 8.2. Cấu hình máy chủ gửi email

Đường dẫn ở chế độ nhà phát triển:

```text
Cài đặt > Kỹ thuật > Email > Máy chủ gửi email
```

Ví dụ cấu hình Gmail:

```text
Mô tả: Gmail SMTP
Máy chủ SMTP: smtp.gmail.com
Cổng SMTP: 587
Bảo mật kết nối: TLS (STARTTLS)
Tên đăng nhập: company@gmail.com
Mật khẩu: App Password của Gmail
Độ ưu tiên: 10
```

Bước thực hiện:

1. Tạo mới máy chủ gửi email.
2. Nhập thông tin SMTP.
3. Bấm `Kiểm tra kết nối`.
4. Lưu cấu hình nếu kiểm tra thành công.

Kết quả mong đợi:

- Odoo báo kết nối thành công.
- Odoo có thể gửi email thật ra ngoài.

Lưu ý Gmail:

- Gmail phải bật xác thực 2 lớp.
- Phải tạo App Password trong Google Account.
- Không dùng mật khẩu đăng nhập Gmail thông thường.

### 8.3. Cấu hình email người nhận

Đường dẫn:

```text
Cài đặt > Người dùng & Công ty > Người dùng
```

Bước thực hiện:

1. Mở user tạo Công việc.
2. Kiểm tra field email có email thật.
3. Mở user được phân công.
4. Kiểm tra field email có email thật.
5. Mở user người kiểm tra.
6. Kiểm tra field email có email thật.

Kết quả mong đợi:

- Người tạo Công việc, người được phân công và người kiểm tra đều có email hợp lệ.
- Email có thể là Gmail thật để kiểm thử nhận email.

### 8.4. Kiểm tra hàng đợi email

Đường dẫn:

```text
Cài đặt > Kỹ thuật > Email > Email
```

Kết quả mong đợi:

- Email gửi thành công có trạng thái đã gửi.
- Email lỗi có thông tin lỗi SMTP để xử lý.

## 9. Kiểm thử email khi đổi giai đoạn công việc

Điều kiện setup:

- Dự án có bộ giai đoạn mặc định của module:
  - `Đang thực hiện`: `is_processing = True`
  - `Chờ kiểm tra`: `is_test = True`
  - `Hoàn thành`: `is_done = True`
- Không chọn `Mẫu email` trên màn hình giai đoạn công việc.
- Chuyển Công việc từ giai đoạn khác sang giai đoạn cần test để kích hoạt email.
- Người tạo Công việc có email.
- Người dùng trong `user_ids` có email.
- Người dùng trong `reviewer_ids` có email.
- Máy chủ gửi email hoạt động hoặc kiểm thử bằng hàng đợi email trong menu kỹ thuật.

Trường hợp kiểm thử TC-PROJ-008: Email khi chuyển sang đang thực hiện

Bước thực hiện:

1. Mở Công việc.
2. Chuyển Công việc sang giai đoạn `Đang thực hiện`.
3. Kiểm tra email gửi ra hoặc hàng đợi email.

Kết quả mong đợi:

- Mẫu email `Email: Đang thực hiện` được dùng.
- Người nhận là `create_uid.email`.
- Nội dung có tên Công việc, nhân sự thực hiện và link mở Công việc.

Trường hợp kiểm thử TC-PROJ-009: Email khi chuyển sang chờ kiểm tra

Bước thực hiện:

1. Gán người kiểm tra cho Công việc.
2. Chuyển Công việc sang giai đoạn `Chờ kiểm tra`.
3. Kiểm tra email gửi ra hoặc hàng đợi email.

Kết quả mong đợi:

- Mẫu email `Email: Chờ kiểm tra` được dùng.
- Người nhận là email của `reviewer_ids`.
- Nội dung có tên Công việc và link mở Công việc.

Trường hợp kiểm thử TC-PROJ-010: Email khi chuyển sang hoàn thành

Bước thực hiện:

1. Gán người được phân công vào Công việc.
2. Chuyển Công việc sang giai đoạn `Hoàn thành`.
3. Kiểm tra email gửi ra hoặc hàng đợi email.

Kết quả mong đợi:

- Mẫu email `Email: Hoàn thành` được dùng.
- Người nhận là `create_uid.email` và email của `user_ids`.
- Nội dung có thông báo Công việc đã hoàn thành và đề nghị đưa lên môi trường Live.

Trường hợp kiểm thử TC-PROJ-011: Không gửi email nếu người dùng không có email

Bước thực hiện:

1. Gán người kiểm tra không có email.
2. Chuyển Công việc sang giai đoạn `Chờ kiểm tra`.
3. Kiểm tra nhật ký hoặc hàng đợi email.

Kết quả mong đợi:

- Không tạo email lỗi.
- Hệ thống bỏ qua người nhận không có email.

## 10. Kiểm thử cron nhắc việc hằng ngày

Đường dẫn ở chế độ nhà phát triển:

```text
Cài đặt > Kỹ thuật > Tự động hóa > Tác vụ đã lên lịch
```

Trường hợp kiểm thử TC-PROJ-012: Cron nhắc Công việc đang thực hiện

Bước thực hiện:

1. Tạo Công việc ở giai đoạn `Đang thực hiện`.
2. Đảm bảo Công việc có người tạo và người được giao có email.
3. Mở cron `Nhắc việc hàng ngày`.
4. Bấm `Chạy thủ công`.

Kết quả mong đợi:

- Gửi mẫu email `Nhắc việc hàng ngày: Đang thực hiện`.
- Người nhận gồm người tạo Công việc và `user_ids`.

Trường hợp kiểm thử TC-PROJ-013: Cron nhắc Công việc chờ kiểm tra

Bước thực hiện:

1. Tạo Công việc ở giai đoạn `Chờ kiểm tra`.
2. Gán người được giao và người kiểm tra có email.
3. Chạy cron thủ công.

Kết quả mong đợi:

- Gửi mẫu email `Nhắc việc hàng ngày: Chờ kiểm tra`.
- Người nhận gồm người tạo Công việc, `user_ids`, `reviewer_ids`.

Trường hợp kiểm thử TC-PROJ-014: Cron nhắc Công việc hoàn thành nhưng chưa lên Live

Bước thực hiện:

1. Tạo Công việc ở giai đoạn `Hoàn thành`.
2. Đảm bảo Công việc chưa chuyển sang giai đoạn `Đã đưa lên Live`.
3. Chạy cron thủ công.

Kết quả mong đợi:

- Gửi mẫu email `Nhắc việc hàng ngày: Hoàn thành chưa lên Live`.
- Người nhận gồm người tạo Công việc và `user_ids`.

Trường hợp kiểm thử TC-PROJ-015: Công việc đã lên Live không vào nhóm chưa lên Live

Bước thực hiện:

1. Tạo Công việc ở giai đoạn `Đã đưa lên Live`.
2. Đảm bảo giai đoạn này có cờ `Đã đưa lên Live`.
3. Chạy cron thủ công.

Kết quả mong đợi:

- Công việc này không nhận email `Nhắc việc hàng ngày: Hoàn thành chưa lên Live`.

## 11. Kiểm thử link Công việc trong email

Trường hợp kiểm thử TC-PROJ-016: Link mở đúng Công việc

Bước thực hiện:

1. Gửi một email thông báo bất kỳ.
2. Mở email.
3. Bấm link `Mở công việc`.

Kết quả mong đợi:

- Link có dạng `/web#id=<task_id>&model=project.task&view_type=form`.
- Trình duyệt mở đúng Công việc tương ứng.

## 12. Danh sách nghiệm thu nhanh

- [ ] Module cài đặt hoặc nâng cấp không lỗi.
- [ ] Đã cấu hình `Email gửi thông báo` và `Tên người gửi`.
- [ ] Đã cấu hình máy chủ gửi email nếu cần gửi email thật.
- [ ] Đã kiểm tra kết nối SMTP thành công.
- [ ] Dự án có trường `Cơ hội`.
- [ ] Cơ hội đã thắng tạo hoặc liên kết Dự án đúng.
- [ ] Bấm smart button `Dự án` trên Cơ hội, kiểm tra mở đúng Công việc của Project.
- [ ] Cơ hội chuyển lại trạng thái đã thắng không tạo trùng Dự án.
- [ ] Dự án mới có đầy đủ giai đoạn mặc định.
- [ ] Giai đoạn công việc có 4 cờ trạng thái.
- [ ] Công việc có danh sách người kiểm tra, thời gian dự kiến hoàn thành và thời gian thực tế hoàn thành.
- [ ] Tab `Checklist` hiển thị và lưu được dòng kiểm tra.
- [ ] Đổi giai đoạn sang đang thực hiện gửi email cho người tạo.
- [ ] Đổi giai đoạn sang chờ kiểm tra gửi email cho người kiểm tra.
- [ ] Đổi giai đoạn sang hoàn thành gửi email cho người tạo và người được giao.
- [ ] Cron đang thực hiện gửi nhắc việc đúng người nhận.
- [ ] Cron chờ kiểm tra gửi nhắc việc đúng người nhận.
- [ ] Cron hoàn thành nhưng chưa lên Live gửi nhắc việc đúng người nhận.
- [ ] Giai đoạn hoàn thành và đã đưa lên Live không bị nhắc chưa lên Live.

## 13. Xử lý lỗi thường gặp

Không thấy module trong Ứng dụng:

1. Kiểm tra `addons_path` có chứa thư mục `E:\DM-Group\doimoi`.
2. Bật chế độ nhà phát triển.
3. Vào `Ứng dụng` và bấm `Cập nhật danh sách ứng dụng`.

Không thấy trường hoặc giao diện mới:

1. Nâng cấp module `dcg_project_customize`.
2. Tải lại trình duyệt bằng `Ctrl + F5`.
3. Kiểm tra người dùng có quyền Dự án phù hợp.

Email không gửi:

1. Kiểm tra người nhận có email.
2. Kiểm tra máy chủ gửi email.
3. Kiểm tra `Cài đặt > Kỹ thuật > Email > Email`.
4. Kiểm tra Stage của Công việc có đúng một cờ nghiệp vụ phù hợp.
5. Kiểm tra Stage đó thuộc đúng Dự án của Công việc, hoặc là Stage dùng chung.
6. Chuyển Công việc sang Stage khác rồi chuyển lại Stage cần test.
7. Kiểm tra mẫu email của module còn hoạt động và không bị sửa sai.

Cron không chạy đúng 08:00:

1. Kiểm tra múi giờ máy chủ và múi giờ người dùng.
2. Kiểm tra `nextcall` của cron `Nhắc việc hàng ngày`.
3. Nếu máy chủ dùng UTC, `01:00:00` tương ứng 08:00 giờ Việt Nam.

## 14. Kiểm tra trước khi commit

1. Chạy kiểm tra Python và XML cho module.
2. Chạy `git status --short`.
3. Chỉ stage thư mục `dcg_project_customize`.
4. Chạy `git diff --cached --name-only`.
5. Đảm bảo danh sách file staged chỉ nằm trong `dcg_project_customize/`.
6. Tạo commit riêng cho module.
