# DCG - Bài học kinh nghiệm dự án

Module: `dcg_project_lessons`

Phiên bản Odoo: `19.0`

## Phạm vi

Module triển khai chức năng **Bài học kinh nghiệm của dự án** theo đặc tả `spec_dcg_modules.docx`.

Mục tiêu của module là ghi nhận, quản lý và tái sử dụng kinh nghiệm triển khai sau mỗi giai đoạn hoặc khi kết thúc dự án. Mỗi bài học được gắn với Project, có thể liên kết thêm Task và Milestone, có phân loại, mức ưu tiên, tag, file đính kèm và chatter.

## Phụ thuộc

- `project`
- `mail`

Module dùng các model chuẩn của Odoo Project:

- `project.project`
- `project.task`
- `project.milestone`
- `project.tags`

## Model chính

Model mới:

```text
project.lesson
```

Các field chính:

| Field | Mô tả |
| --- | --- |
| `project_id` | Dự án liên quan, bắt buộc |
| `name` | Tiêu đề bài học |
| `category` | Nghiệp vụ, Kỹ thuật, Hạ tầng, Triển khai, Hiệu năng, Bảo mật, Kiểm thử, Đào tạo, Khách hàng, Khác |
| `module` | Tên module Odoo liên quan |
| `task_id` | Task liên quan, lọc theo Project |
| `milestone_id` | Milestone liên quan, lọc theo Project |
| `priority` | Normal, Important, Critical |
| `problem` | Vấn đề đã xảy ra, bắt buộc |
| `cause` | Nguyên nhân gốc rễ |
| `solution` | Giải pháp đã áp dụng |
| `result` | Kết quả sau khi áp dụng |
| `recommendation` | Khuyến nghị cho dự án tiếp theo |
| `tag_ids` | Tag phân loại, dùng `project.tags` |
| `attachment_ids` | File đính kèm |
| `author_id` | Người tạo |
| `date` | Ngày ghi nhận |
| `state` | Nháp, Đã xác nhận, Đã lưu trữ |

## Luồng trạng thái

```text
Nháp -> Đã xác nhận -> Đã lưu trữ
```

Action đã triển khai:

- `action_confirm`: xác nhận bài học từ Nháp sang Đã xác nhận.
- `action_archive_lesson`: chuyển bài học sang Đã lưu trữ.
- `action_unarchive_lesson`: đưa bài học Đã lưu trữ về Nháp để chỉnh sửa lại.

Chỉ Project Manager, Director hoặc System Admin được confirm/archive/unarchive.

Chỉ lesson ở trạng thái `archived` mới được xóa.

## Liên kết ngược

Module kế thừa các model sau:

- `project.project`
- `project.task`
- `project.milestone`

Các form được bổ sung smart button:

- Form dự án: `Bài học kinh nghiệm (N)`
- Task form: `Lessons (N)`
- Milestone form: `Lessons (N)`

Khi tạo Lesson từ smart button Project, `project_id` được set mặc định từ context.

## Menu và Views

Menu:

```text
Dự án > Bài học kinh nghiệm
```

Views đã khai báo:

- Kanban, group mặc định theo `state`
- List
- Form, có chatter và attachment
- Pivot
- Graph
- Search view

Search view hỗ trợ:

- Tìm theo tên lesson
- Tìm theo module
- Lọc category
- Lọc tag
- Lọc project
- Lọc author
- Lọc trạng thái Nháp / Đã xác nhận / Đã lưu trữ
- Lọc priority Normal / Important / Critical
- Lọc date
- Group by Category, Project, State, Priority, Author

## Cảnh báo khi đóng Project

Module override `project.project.action_archive()`.

Nếu Project còn Lesson ở trạng thái `draft`, hệ thống mở wizard cảnh báo:

```text
Dự án còn bài học kinh nghiệm chưa được xác nhận. Bạn có muốn tiếp tục đóng không?
```

User có thể:

- `Tiep tuc`: tiếp tục archive Project.
- `Hủy để xem lại`: mở danh sách bài học Nháp của dự án.
- `Dong`: đóng wizard.

## Phân quyền

Module tạo 3 nhóm quyền riêng:

- `Bài học kinh nghiệm - Nhân viên`
- `Bài học kinh nghiệm - Quản lý dự án`
- `Bài học kinh nghiệm - Giám đốc`

Quyền hiện tại:

| Nhóm | Quyền |
| --- | --- |
| Nhân viên | Tạo bài học, đọc bài học do mình tạo hoặc thuộc dự án mình quản lý/theo dõi, sửa bài học Nháp do mình tạo |
| Project Manager | Đọc/sửa/tạo lesson thuộc project mình quản lý hoặc theo dõi, confirm/archive lesson |
| Director | Toàn quyền trên tất cả lesson |
| System Admin | Toàn quyền trên tất cả lesson |

Module cũng cấp quyền tạo/sửa `project.tags` cho group Employee của module để dùng quick-create tag trong form.

User nội bộ mới mặc định nhận nhóm `Bài học kinh nghiệm - Nhân viên`; nhóm này kéo theo quyền `Dự án: Người dùng`. Khi nâng cấp module, cấu hình mặc định cũng được áp dụng cho toàn bộ user nội bộ đang hoạt động. Tài khoản Portal không được cấp các quyền này.

## Cấu trúc

```text
dcg_project_lessons/
|-- __init__.py
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   |-- project_lesson.py
|   |-- project_milestone.py
|   |-- project_project.py
|   `-- project_task.py
|-- security/
|   |-- ir.model.access.csv
|   |-- record_rules.xml
|   `-- security_groups.xml
|-- views/
|   |-- menus.xml
|   |-- project_lesson_views.xml
|   |-- project_milestone_views.xml
|   |-- project_project_views.xml
|   `-- project_task_views.xml
|-- wizard/
|   |-- __init__.py
|   |-- project_lesson_archive_warning.py
|   `-- project_lesson_archive_warning_views.xml
|-- README.md
`-- TESTING.md
```

## Nâng cấp module

Lệnh tham khảo:

```powershell
powershell -ExecutionPolicy Bypass -File E:\DM-Group\doimoi\run_odoo19.ps1 -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_lessons --stop-after-init --no-http
```

## Lưu ý kỹ thuật

- Hiện tại module dùng `many2many_binary` cho attachment và có chatter qua `mail.thread`.
- Domain `task_id` và `milestone_id` được lọc theo `project_id`.
- Có constraint Python để chặn lưu Task/Milestone không cùng Project với Lesson.
- Cảnh báo đóng Project xử lý qua `action_archive()`; trường hợp code khác gọi trực tiếp `write({'active': False})` sẽ không trả được wizard UI.
