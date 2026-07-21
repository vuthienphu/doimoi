# DCG - Thông tin triển khai dự án

Module: `dcg_project_deployment`

Phiên bản Odoo: `19.0`

## Phạm vi

Module triển khai chức năng **Quản lý Thông tin Triển khai** theo đặc tả `spec_dcg_modules.docx`.

Module lưu thông tin vận hành gắn với Project, gồm tài khoản đăng nhập và thông tin kết nối máy chủ. Dữ liệu trong module có tính nhạy cảm cao, nên quyền truy cập được giới hạn chặt theo nhóm Odoo.

## Phụ thuộc

- `project`
- `mail`

## Model chính

Model mới:

```text
project.account
project.remote
```

## `project.account`

Model lưu tài khoản đăng nhập theo Project.

Các field chính:

| Field | Mô tả |
| --- | --- |
| `project_id` | Project liên quan, bắt buộc |
| `name` | Tên mô tả tài khoản |
| `account_type` | Admin, Test, User, Readonly, API, Database, FTP, Email, Other |
| `username` | Tên đăng nhập |
| `password` | Mật khẩu thật, chỉ System Admin đọc được |
| `password_masked` | Mật khẩu đã che, hiển thị `***` cho Quản lý dự án khi tài khoản có mật khẩu |
| `url` | URL truy cập |
| `note` | Ghi chú |
| `active` | Archive account khi không còn dùng |

Tên đăng nhập dùng widget `CopyClipboardChar`.

Mật khẩu dùng:

- `widget="password"` để ẩn ký tự.
- `CopyClipboardButton` cho System Admin copy password.

## `project.remote`

Model lưu thông tin kết nối máy chủ theo Project.

Các field chính:

| Field | Mô tả |
| --- | --- |
| `project_id` | Project liên quan, bắt buộc |
| `name` | Tên mô tả kết nối |
| `server_type` | Linux, Windows Server, NAS, Docker, Cloud, Other |
| `connection_type` | SSH, RDP, UltraViewer, AnyDesk, TeamViewer, Webpanel, FTP, SFTP, Database, VPN, Other |
| `host` | IP hoặc hostname |
| `port` | Port |
| `username` | Tên đăng nhập |
| `password` | Mật khẩu, chỉ Quản trị hệ thống đọc được |
| `private_key` | Khóa riêng SSH/VPN, chỉ Quản trị hệ thống đọc được |
| `path` | Đường dẫn thư mục |
| `url` | URL control panel |
| `partner_id_field` | Partner ID / TeamViewer ID |
| `address_field` | AnyDesk Address / ID |
| `database` | Tên database |
| `note` | Ghi chú |
| `active` | Archive remote khi không còn dùng |

Form `project.remote` hiển thị field động theo `connection_type`.

## Liên kết với Project

Module kế thừa `project.project` và thêm:

- `account_ids`
- `remote_ids`
- `account_count`
- `remote_count`

Project form có 2 smart button:

- `Tài khoản (N)`: hiển thị với Quản lý dự án và Quản trị hệ thống.
- `Kết nối máy chủ (N)`: chỉ hiển thị với Quản trị hệ thống.

## Menu và Views

Menu:

```text
Dự án > Triển khai > Tài khoản
Dự án > Triển khai > Kết nối máy chủ
```

Menu `Triển khai` và `Tài khoản` chỉ hiển thị với Quản lý dự án/Quản trị hệ thống.

Menu `Kết nối máy chủ` chỉ hiển thị với Quản trị hệ thống.

Views đã khai báo:

- Account list/form/search
- Remote list/form/search

Search hỗ trợ:

- Account: name, project, account type, username, url, active/archived, group by project/account type.
- Remote: name, project, server type, connection type, host, url, active/archived, group by project/server type/connection type.

## Phân quyền

| Nhóm | `project.account` | `project.remote` |
| --- | --- | --- |
| System Admin (`base.group_system`) | Read/Create/Write/Delete, thấy password thật | Read/Create/Write/Delete, thấy toàn bộ field nhạy cảm |
| Project Manager | Read-only account, password hiển thị `***` qua `password_masked` | Không có quyền |
| Employee | Không có quyền | Không có quyền |

Password/private key thật có `groups='base.group_system'` trên field model để PM không đọc được qua RPC/export.

## Bảo mật mật khẩu

Hiện tại module đã chặn truy cập field nhạy cảm bằng quyền Odoo nhưng **chưa mã hóa password/private_key trước khi lưu DB**.

Backlog bắt buộc trước go-live nếu lưu dữ liệu thật:

- Mã hóa `password` và `private_key` bằng Fernet/AES.
- Key lấy từ biến môi trường hoặc `ir.config_parameter`.
- Không hardcode key trong source.
- Không commit dữ liệu password thật vào git.

## Cấu trúc

```text
dcg_project_deployment/
|-- __init__.py
|-- __manifest__.py
|-- models/
|   |-- __init__.py
|   |-- project_account.py
|   |-- project_project.py
|   `-- project_remote.py
|-- security/
|   |-- ir.model.access.csv
|   `-- record_rules.xml
|-- views/
|   |-- menus.xml
|   |-- project_account_views.xml
|   |-- project_project_views.xml
|   `-- project_remote_views.xml
|-- README.md
`-- TESTING.md
```

## Nâng cấp module

Lệnh tham khảo:

```powershell
powershell -ExecutionPolicy Bypass -File E:\DM-Group\doimoi\run_odoo19.ps1 -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_deployment --stop-after-init --no-http
```
