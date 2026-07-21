# DCG Project Dashboard

Module: `dcg_project_dashboard`

Phiên bản Odoo: `19.0`

## Phạm vi

Module triển khai **Phần B: Dashboard quản trị dự án** theo đặc tả `dcg_project_customize_BA_DEV`.

Dashboard phục vụ Ban giám đốc và quản lý dự án, hiển thị KPI, tiến độ, workload và các danh sách Task cần theo dõi. Dashboard không dùng Pivot, Graph hay Spreadsheet; giao diện được xây dựng bằng OWL/XML/JS/CSS và lấy dữ liệu qua JSON API.

## Phụ thuộc

- `project`
- `web`
- `dcg_project_customize`

Module phụ thuộc `dcg_project_customize` vì Dashboard dùng các cờ Stage:

- `project.task.type.is_processing`
- `project.task.type.is_test`
- `project.task.type.is_done`
- `project.task.type.is_live`

## Menu và phân quyền

Menu:

```text
Dashboard Dự án
```

Module này là app độc lập trên màn hình chính Odoo, không nằm trong app `Dự án` / `Project`.

Không kiểm thử module này trong app `Báo cáo tổng quan` mặc định của Odoo. Màn `Báo cáo tổng quan` có URL dạng `/odoo/dashboards?...` là dashboard/report mặc định của Odoo từ module `spreadsheet_dashboard`, không phải màn hình của `dcg_project_dashboard`.

Nhóm được phép truy cập menu:

- `project.group_project_manager`
- `dcg_project_dashboard.group_project_dashboard_director`

## Bỏ Dashboard mặc định của Odoo

App `Báo cáo tổng quan` / `Dashboards` mặc định của Odoo đến từ module `spreadsheet_dashboard`.

Cách bỏ khỏi giao diện:

1. Vào `Apps`.
2. Bỏ filter `Apps` nếu cần, tìm module `Spreadsheet dashboard`.
3. Chọn `Uninstall` nếu hệ thống không dùng dashboard spreadsheet mặc định.

Cách chỉ ẩn menu mà không gỡ module:

1. Bật Developer mode.
2. Vào `Settings > Technical > User Interface > Menu Items`.
3. Tìm menu `Dashboards` có XML ID `spreadsheet_dashboard.spreadsheet_dashboard_menu_root`.
4. Archive menu này hoặc giới hạn nhóm quyền để user thường không thấy.

Không sửa trực tiếp source Odoo gốc để ẩn menu mặc định, vì khi update Odoo có thể bị ghi đè.

## Bộ lọc

Dashboard có các bộ lọc:

- Khoảng thời gian: Hôm nay, Hôm qua, 7 ngày, 30 ngày, Tuần này, Tháng này, Quý này, Năm nay.
- Từ ngày, Đến ngày.
- Kiểu thống kê: Ngày tạo Project, Ngày tạo Task, Deadline, Ngày hoàn thành, Ngày đưa Live.
- Dự án.
- Khách hàng.
- PM.
- Nhân sự.
- Stage.

Các bộ lọc nhiều lựa chọn hiển thị dạng tag/chip. Dashboard chỉ dùng 5 Stage chuẩn của module `dcg_project_customize`:

- `Cần làm`
- `Đang làm`
- `Chuyển test`
- `Hoàn thành`
- `Đã đưa lên Live`

## API

Các API đã triển khai:

| API | Chức năng |
| --- | --- |
| `/dashboard/options` | Dữ liệu cho bộ lọc |
| `/dashboard/summary` | KPI tổng hợp |
| `/dashboard/project` | Danh sách và thông tin dự án |
| `/dashboard/task_stage` | Phân bố Task theo Stage |
| `/dashboard/task_trend` | Xu hướng Task theo ngày |
| `/dashboard/workload` | Khối lượng công việc nhân sự |
| `/dashboard/project_progress` | Bảng tiến độ dự án |
| `/dashboard/overdue` | Task quá hạn |
| `/dashboard/testing` | Task chuyển test |
| `/dashboard/not_live` | Task hoàn thành nhưng chưa đưa Live |
| `/dashboard/upcoming` | Task sắp đến hạn |

Các API dùng cache nội bộ 45 giây theo user, endpoint và filter.

## Thành phần giao diện

Dashboard hiện có:

- Nhóm KPI tổng hợp.
- Dải chỉ số Task theo 5 Stage chuẩn.
- Donut chart phân bố Task theo Stage.
- Line chart xu hướng Task tạo mới, hoàn thành và quá hạn.
- Bảng tiến độ Project, có progress bar, Stage bung đủ 5 Stage chuẩn và sắp xếp theo cột.
- Workload nhân sự, có avatar, badge quá hạn, mini progress bar phần trăm và sắp xếp theo cột.
- Danh sách Task quá hạn, có avatar người thực hiện, badge số ngày trễ và giới hạn 2 dòng cho tên Task/Dự án.
- Danh sách Task sắp đến hạn, có avatar người thực hiện, badge cảnh báo và giới hạn 2 dòng cho tên Task/Dự án.
- Danh sách Task chuyển test.
- Danh sách Task chưa đưa Live.

## Dữ liệu demo

DB `Odoo19CRM` đã được seed dữ liệu demo có prefix `DCG Demo -` để kiểm thử dashboard:

- 6 khách hàng.
- 8 user/nhân sự.
- 12 project.
- 120 task phân bổ vào 5 Stage chuẩn.

Phân bổ Stage demo hiện tại:

| Stage | Số Task | Tỷ lệ |
| --- | ---: | ---: |
| Cần làm | 24 | 20% |
| Đang làm | 36 | 30% |
| Chuyển test | 24 | 20% |
| Hoàn thành | 24 | 20% |
| Đã đưa lên Live | 12 | 10% |

## Cấu trúc

```text
dcg_project_dashboard/
|-- __init__.py
|-- __manifest__.py
|-- controllers/
|   |-- __init__.py
|   `-- dashboard.py
|-- models/
|   `-- __init__.py
|-- services/
|   |-- __init__.py
|   `-- project_dashboard_service.py
|-- static/
|   |-- description/icon.svg
|   `-- src/
|       |-- css/project_dashboard.css
|       |-- js/project_dashboard.js
|       `-- xml/project_dashboard.xml
|-- security/
|   `-- security.xml
`-- views/
    `-- dashboard_views.xml
```

## Lưu ý kỹ thuật

- Dashboard dùng `read_group()` cho các thống kê theo Stage, Project và workload.
- Các widget bảng nửa dưới dùng giới hạn Top 10 qua `_WIDGET_ROW_LIMIT = 10`.
- Bảng tiến độ Project giới hạn 2.000 Project theo tiêu chí hiệu năng trong đặc tả.
- Biểu đồ frontend dùng SVG/HTML/CSS, không thêm thư viện JS ngoài.
- API dashboard có cache nội bộ 45 giây theo user, endpoint và filter.
- Frontend có sort nội bộ cho `Bảng tiến độ dự án` và `Workload nhân sự`.

## Nâng cấp module

```powershell
E:\DM-Group\doimoi-master\.venv\Scripts\python.exe E:\DM-Group\odoo19\odoo-bin server -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_dashboard --http-port=8070
```
