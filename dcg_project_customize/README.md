# DCG Project Customize

Module: `dcg_project_customize`

Phiên bản Odoo: `19.0`

## 1. Mục tiêu

Module bổ sung quy trình tạo Dự án từ Cơ hội đã thắng, mở rộng thông tin Công việc, checklist, người kiểm tra, trạng thái giai đoạn công việc và thông báo email theo quy trình phát triển.

## 2. Phụ thuộc

Module phụ thuộc các addon:

- `project`
- `crm`
- `mail`

## 3. Phạm vi nghiệp vụ

### 3.1. Tạo Dự án từ Cơ hội đã thắng

Model kế thừa:

- `crm.lead`
- `project.project`

Field bổ sung:

| Field | Type | Attrs | Mô tả |
| --- | --- | --- | --- |
| `project.project.lead_id` | Many2one `crm.lead` | readonly, copy=False | Cơ hội liên kết với Dự án |
| `crm.lead.project_id` | Many2one `project.project` | readonly, copy=False | Dự án được tạo hoặc liên kết từ Cơ hội |

Trigger tạo hoặc liên kết Dự án:

- Khi Cơ hội được đánh dấu đã thắng bằng action gốc.
- Khi `stage_id` hoặc `probability` thay đổi và Cơ hội đạt điều kiện đã thắng.

Điều kiện xử lý:

- `type == 'opportunity'`
- `probability >= 100` hoặc `stage_id.is_won = True`

Quy tắc:

- Nếu Cơ hội đã có `project_id`, hệ thống dùng lại Dự án đó và gán thêm `project.lead_id` nếu còn trống.
- Nếu đã có Dự án với `lead_id = lead.id`, hệ thống dùng lại Dự án đó.
- Nếu chưa có Dự án, hệ thống tạo Dự án mới với `name`, `partner_id`, `user_id`, `lead_id` lấy từ Cơ hội.
- Field `project_id` trên Cơ hội được dùng làm liên kết kỹ thuật và được ẩn trên form. Người dùng mở Dự án bằng smart button `Dự án`.
- Smart button `Dự án` mở thẳng kanban Công việc của Dự án tương ứng trong app Dự án.

### 3.2. Quy trình Stage mặc định

Model kế thừa: `project.project`

Module tạo sẵn bộ giai đoạn công việc theo quy trình DCG:

| Tên Stage | Cờ trạng thái |
| --- | --- |
| `Cần làm` | Không có cờ |
| `Đang thực hiện` | `is_processing = True` |
| `Chờ kiểm tra` | `is_test = True` |
| `Hoàn thành` | `is_done = True` |
| `Đã đưa lên Live` | `is_live = True` |

Khi cài đặt hoặc nâng cấp module, hệ thống tự gán các giai đoạn mặc định này cho toàn bộ Dự án hiện có. Khi tạo Dự án mới, hệ thống cũng tự gán bộ giai đoạn này vào Dự án mới để người dùng không phải nhập lại Stage hoặc tick cờ trạng thái thủ công.

### 3.3. Trạng thái nghiệp vụ trên Task Stage

Model kế thừa: `project.task.type`

Field bổ sung:

| Field | Type | Default | Mô tả |
| --- | --- | --- | --- |
| `is_processing` | Boolean | `False` | Stage đang thực hiện |
| `is_test` | Boolean | `False` | Stage chờ kiểm tra |
| `is_done` | Boolean | `False` | Stage hoàn thành |
| `is_live` | Boolean | `False` | Stage đã đưa lên Live |

Lưu ý:

- Các flag trạng thái chỉ nằm trên `project.task.type`.
- Công việc xác định trạng thái thông qua `task.stage_id.is_processing`, `task.stage_id.is_test`, `task.stage_id.is_done`, `task.stage_id.is_live`.
- Mỗi Stage nghiệp vụ chỉ nên chọn một flag chính. Ví dụ Stage `Đang thực hiện` chỉ chọn `Đang thực hiện`, Stage `Chờ kiểm tra` chỉ chọn `Chờ kiểm tra`.
- Module không dùng trường `Mẫu email` mặc định của Odoo trên Stage. Email được chọn tự động theo các flag trạng thái ở trên.
- Người dùng chỉ cần chỉnh Stage thủ công nếu muốn đổi tên hoặc mở rộng quy trình ngoài bộ mặc định.

### 3.4. Thông tin bổ sung trên Công việc

Model kế thừa: `project.task`

Field bổ sung:

| Field | Type | Attrs | Mô tả |
| --- | --- | --- | --- |
| `reviewer_ids` | Many2many `res.users` | editable | Danh sách người kiểm tra |
| `planned_finish_date` | Datetime | editable | Thời gian dự kiến hoàn thành |
| `actual_finish_date` | Datetime | editable | Thời gian thực tế hoàn thành |
| `checklist_ids` | One2many `task.checklist` | editable | Danh sách checklist của Công việc |

### 3.5. Checklist Công việc

Model mới: `task.checklist`

| Field | Type | Required | Mô tả |
| --- | --- | --- | --- |
| `sequence` | Integer | No | Thứ tự hiển thị |
| `name` | Char | Yes | Nội dung kiểm tra |
| `is_done` | Boolean | No | Đã hoàn thành |
| `task_id` | Many2one `project.task` | Yes | Công việc cha |

Quy tắc:

- Xóa Công việc sẽ xóa checklist con do `ondelete='cascade'`.
- Checklist hiển thị trong tab `Checklist` trên form Công việc.

## 4. Thông báo email khi đổi giai đoạn Công việc

Trigger:

- Override `project.task.write()`.
- Chỉ xử lý khi `stage_id` thay đổi.

Quy tắc gửi email:

| Điều kiện Stage | Template | Người nhận |
| --- | --- | --- |
| `stage_id.is_processing = True` | `task_processing_notify` | Người tạo Công việc `create_uid` |
| `stage_id.is_test = True` | `task_test_notify` | `reviewer_ids` |
| `stage_id.is_done = True` | `task_done_notify` | Người tạo Công việc + `user_ids` |

Email template:

- Đang thực hiện: gửi tên Công việc, nhân sự thực hiện và link mở Công việc.
- Chờ kiểm tra: gửi tên Công việc và link mở Công việc.
- Hoàn thành: thông báo Công việc đã hoàn thành và đề nghị đưa lên Live.

Nếu không có người nhận có email, module bỏ qua việc gửi mail.

Lưu ý kiểm thử:

- Email chỉ phát sinh khi Công việc được chuyển từ giai đoạn khác sang giai đoạn có flag.
- Stage phải thuộc đúng Dự án của Công việc, hoặc là Stage dùng chung không gán Dự án cụ thể.
- Các email tiêu đề `My Company: Your Odoo Periodic Digest` là email định kỳ mặc định của Odoo, không phải email của module này.

## 5. Cron nhắc việc hằng ngày

Cron: `cron_daily_task_reminder`

Method: `project.task._cron_send_daily_reminders()`

Lịch chạy:

- `interval_number = 1`
- `interval_type = days`
- `nextcall = 2025-01-01 01:00:00`

Với server dùng UTC, `01:00:00` tương ứng 08:00 giờ Việt Nam.

Nhóm nhắc việc:

| Điều kiện Công việc | Template | Người nhận |
| --- | --- | --- |
| `stage_id.is_processing = True` | `task_reminder_processing` | Người tạo Công việc + `user_ids` |
| `stage_id.is_test = True` | `task_reminder_test` | Người tạo Công việc + `user_ids` + `reviewer_ids` |
| `stage_id.is_done = True` và `stage_id.is_live = False` | `task_reminder_done_not_live` | Người tạo Công việc + `user_ids` |

## 6. View đã kế thừa

### 6.1. Project

File: `views/project_project_views.xml`

Kế thừa:

- `project.edit_project`

Thay đổi:

- Thêm field `lead_id` sau `partner_id`.

### 6.2. Task Stage

File: `views/project_task_type_views.xml`

Kế thừa:

- `project.task_type_edit`

Thay đổi:

- Thêm các flag `is_processing`, `is_test`, `is_done`, `is_live` sau field `fold`.

### 6.3. Task

File: `views/project_task_views.xml`

Kế thừa:

- `project.view_task_form2`

Thay đổi:

- Thêm `reviewer_ids`, `planned_finish_date`, `actual_finish_date` sau `user_ids`.
- Thêm tab `Checklist` sau tab mô tả.

### 6.4. Cấu hình email gửi thật

File: `views/res_config_settings_views.xml`

Kế thừa:

- `project.res_config_settings_view_form`

Thay đổi:

- Thêm block `Email thông báo DCG` trong app `Project` của màn hình Settings.
- Thêm trường `Email gửi thông báo`.
- Thêm trường `Tên người gửi`.

## 7. Thiết kế gửi email thật

Module gửi email qua cơ chế mail chuẩn của Odoo:

- Các template dùng `mail.template`.
- Khi đổi giai đoạn Task hoặc chạy cron, module gọi `send_mail(..., force_send=True)`.
- Email đi ra ngoài được gửi bằng `Outgoing Mail Server` đang cấu hình trong Odoo.

Email người gửi được xác định theo thứ tự:

1. `Email gửi thông báo` trong `Settings > Project > Email thông báo DCG`.
2. Email của công ty hiện tại.
3. Email của user đang chạy thao tác.

Tên người gửi được xác định theo thứ tự:

1. `Tên người gửi` trong `Settings > Project > Email thông báo DCG`.
2. Tên công ty hiện tại.
3. Tên user đang chạy thao tác.

Để gửi email thật tới Gmail hoặc email bên ngoài, cần cấu hình SMTP:

```text
Cài đặt > Kỹ thuật > Email > Máy chủ gửi email
```

Ví dụ Gmail SMTP:

```text
SMTP Server: smtp.gmail.com
SMTP Port: 587
Connection Security: TLS (STARTTLS)
Username: company@gmail.com
Password: App Password của Gmail
```

Lưu ý:

- Gmail phải bật xác thực 2 lớp và dùng App Password, không dùng mật khẩu đăng nhập thường.
- Email người nhận phải được khai báo trên user Odoo.
- Nếu chưa cấu hình Outgoing Mail Server, email có thể chỉ nằm trong hệ thống Odoo hoặc báo lỗi gửi.
- Nên dùng email công ty hoặc email no-reply để gửi, ví dụ `noreply@company.com`.

## 8. Security

File: `security/ir.model.access.csv`

Access đã khai báo:

| Model | Group | Read | Write | Create | Delete |
| --- | --- | --- | --- | --- | --- |
| `task.checklist` | `project.group_project_user` | 1 | 1 | 1 | 1 |
| `task.checklist` | `project.group_project_manager` | 1 | 1 | 1 | 1 |
| `project.task.type` | `project.group_project_manager` | 1 | 1 | 1 | 0 |

Lưu ý:

- Quyền Odoo là cộng dồn. Dòng `project.task.type` với `Delete = 0` không thu hồi quyền xóa nếu module khác đã cấp quyền xóa.

## 9. Đối chiếu đặc tả

| Hạng mục đặc tả | Trạng thái triển khai |
| --- | --- |
| Cơ hội đã thắng tạo hoặc liên kết Dự án | Đã xử lý trong `crm.lead`, có chống tạo trùng theo `project_id` và `lead_id` |
| Dự án lưu ngược Cơ hội | Đã có `project.project.lead_id` |
| Dự án mới có đầy đủ Stage mặc định | Đã có `data/stage_data.xml` và tự gán cho Dự án hiện có hoặc Dự án mới |
| Trạng thái nằm trên `project.task.type` | Đã có `is_processing`, `is_test`, `is_done`, `is_live`; không thêm trạng thái nghiệp vụ vào `project.task` |
| Công việc có người kiểm tra, ngày dự kiến, ngày thực tế, checklist | Đã có `reviewer_ids`, `planned_finish_date`, `actual_finish_date`, `checklist_ids` |
| Email khi sang `Đang thực hiện` | Gửi `Email: Đang thực hiện` cho người tạo Công việc |
| Email khi sang `Chờ kiểm tra` | Gửi `Email: Chờ kiểm tra` cho `reviewer_ids` |
| Email khi sang `Hoàn thành` | Gửi `Email: Hoàn thành` cho người tạo và người được giao |
| Cron 08:00 hằng ngày | Đã có cron `Nhắc việc hàng ngày`, `nextcall = 2025-01-01 01:00:00` tương ứng 08:00 giờ Việt Nam nếu server dùng UTC |
| Cron nhắc 3 nhóm | Đã nhắc `Đang thực hiện`, `Chờ kiểm tra`, `Hoàn thành chưa lên Live` đúng nhóm người nhận |

## 10. Cấu trúc file

```text
dcg_project_customize/
|-- __init__.py
|-- __manifest__.py
|-- README.md
|-- TESTING.md
|-- data/
|   |-- cron_data.xml
|   |-- mail_template.xml
|   `-- stage_data.xml
|-- models/
|   |-- __init__.py
|   |-- crm_lead.py
|   |-- project_project.py
|   |-- res_config_settings.py
|   |-- project_task.py
|   |-- project_task_type.py
|   `-- task_checklist.py
|-- security/
|   `-- ir.model.access.csv
`-- views/
    |-- crm_lead_views.xml
    |-- project_project_views.xml
    |-- res_config_settings_views.xml
    |-- project_task_type_views.xml
    `-- project_task_views.xml
```

## 11. Checklist test nhanh

- [ ] Cài đặt hoặc nâng cấp module `dcg_project_customize`.
- [ ] Cấu hình Outgoing Mail Server nếu cần gửi email thật.
- [ ] Cấu hình `Email gửi thông báo` và `Tên người gửi` trong Settings > Project.
- [ ] Mở Dự án, kiểm tra field `Cơ hội`.
- [ ] Đánh dấu Cơ hội đã thắng, kiểm tra Dự án được tạo hoặc liên kết đúng.
- [ ] Bấm smart button `Dự án` trên Cơ hội, kiểm tra mở đúng kanban Công việc của Dự án.
- [ ] Cơ hội đã có Dự án thì đánh dấu đã thắng lại không tạo trùng.
- [ ] Tạo Dự án mới, kiểm tra 5 Stage mặc định được gán vào Dự án.
- [ ] Mở Task Stage, kiểm tra các flag trạng thái đã được cấu hình sẵn.
- [ ] Mở Công việc, kiểm tra các field người kiểm tra và ngày hoàn thành.
- [ ] Thêm checklist trên tab `Checklist`.
- [ ] Chuyển Công việc sang `Đang thực hiện`, kiểm tra email người tạo.
- [ ] Chuyển Công việc sang `Chờ kiểm tra`, kiểm tra email người kiểm tra.
- [ ] Chuyển Công việc sang `Hoàn thành`, kiểm tra email người tạo và người được giao.
- [ ] Chạy cron `Nhắc việc hàng ngày`, kiểm tra email nhắc theo từng nhóm.

## 12. Lưu ý kỹ thuật

- Module định nghĩa `project_id` trên `crm.lead` để lưu liên kết kỹ thuật tới Dự án và ẩn field này trên form Cơ hội.
- Module không phụ thuộc trực tiếp vào `dcg_custom_crm`.
- Email chỉ gửi cho user có email.
- Email gửi ra ngoài phụ thuộc cấu hình Outgoing Mail Server của Odoo.
- Email người gửi lấy từ cấu hình `Email thông báo DCG`, sau đó fallback về email công ty hoặc email user.
- Link Công việc lấy từ `web.base.url`.
- Sau khi sửa XML, view hoặc template, cần nâng cấp module và refresh browser.

## 13. Commit riêng module

Mục tiêu là chỉ commit thư mục `dcg_project_customize`, không đưa các thay đổi của module khác hoặc file môi trường vào commit.

Kiểm tra trạng thái:

```powershell
git status --short
```

Stage riêng module:

```powershell
git add -- dcg_project_customize
```

Kiểm tra danh sách file sẽ commit:

```powershell
git diff --cached --name-only
```

Nếu danh sách chỉ nằm trong `dcg_project_customize/`, tạo commit:

```powershell
git commit -m "Add DCG project customization"
```

Không dùng `git add .` trong lần commit này vì repository đang có thay đổi ngoài module như cấu hình local, dữ liệu Odoo hoặc theme khác.
