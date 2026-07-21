# DCG Project Customize

Module: `dcg_project_customize`

Phiên bản Odoo: `19.0`

## Phạm vi đã hoàn thành: Phần A

Module đã triển khai phần **Chuẩn hóa Stage của Dự án** theo đặc tả `dcg_project_customize_BA_DEV`.

Mục tiêu của phần này là chuẩn hóa `project.task.type` để các Dự án dùng chung bộ Stage thống nhất, tránh việc mỗi Project sinh một bộ Stage rời rạc và gây khó thống kê.

## Stage mặc định

Khi cài đặt hoặc nâng cấp module, hệ thống tạo và chuẩn hóa 5 Stage mặc định:

| STT | Tên Stage | Cờ nghiệp vụ |
| --- | --- | --- |
| 1 | `Cần làm` | Không có cờ |
| 2 | `Đang làm` | `is_processing = True` |
| 3 | `Chuyển test` | `is_test = True` |
| 4 | `Hoàn thành` | `is_done = True` |
| 5 | `Đã đưa lên Live` | `is_live = True` |

File dữ liệu: `data/stage_data.xml`.

## Cơ chế đồng bộ Stage với Project

Theo yêu cầu triển khai thực tế của dự án, các Stage vẫn được gắn vào Project thông qua `project_ids`.

Module xử lý 3 luồng chính:

- Khi tạo `project.project` mới, hệ thống add Project mới vào tất cả record `project.task.type`.
- Khi quản trị viên tạo `project.task.type` mới, hệ thống add Stage mới vào tất cả Project hiện có.
- Khi cài đặt hoặc nâng cấp module, hệ thống đồng bộ lại toàn bộ Stage với toàn bộ Project hiện có.

Các phần xử lý chính:

- `models/project_project.py`: override `project.project.create()` và method `_dcg_assign_all_stages_to_all_projects()`.
- `models/project_task_type.py`: override `project.task.type.create()`.
- `data/stage_data.xml`: gọi function đồng bộ khi load data.

## Sửa tên Stage

Các Project dùng chung record `project.task.type`. Vì vậy khi quản trị viên sửa tên Stage, tên mới được áp dụng đồng bộ ở tất cả Project đang dùng Stage đó.

Không cần override riêng `write()` cho nghiệp vụ sửa tên Stage.

## Xóa Stage

Module chặn xóa Stage nếu Stage đang được Task sử dụng.

Thông báo lỗi:

```text
Stage đang được sử dụng.
```

Logic nằm trong `models/project_task_type.py`, method `unlink()`.

## Cleanup dữ liệu Stage trùng

Module có migration/cleanup để gom các Stage trùng từ dữ liệu cũ.

Method:

```text
project.task.type._dcg_cleanup_duplicate_stages()
```

Method này được gọi khi nâng cấp module qua `data/stage_data.xml`.

Cleanup xử lý:

- Gom Stage theo các nhóm tên chuẩn và tên cũ:
  - `Đang làm` nhận cả Stage cũ `Đang thực hiện`.
  - `Chuyển test` nhận cả Stage cũ `Chờ kiểm tra`.
- Ưu tiên giữ record chuẩn theo XML ID của module.
- Merge `project_ids` từ Stage trùng vào Stage chuẩn.
- Chuyển toàn bộ `project.task.stage_id` từ Stage trùng sang Stage chuẩn.
- Xóa các Stage trùng sau khi Task đã được map lại.
- Không gửi email khi migration đổi `stage_id`.

## Đối chiếu Phần A

| Yêu cầu | Trạng thái |
| --- | --- |
| Tạo 5 Stage mặc định | Đã làm |
| Giữ các field `is_processing`, `is_test`, `is_done`, `is_live` | Đã làm |
| Khi tạo Project mới, Project dùng được toàn bộ Stage | Đã làm |
| Khi tạo Stage mới, tất cả Project dùng được Stage mới | Đã làm |
| Khi sửa tên Stage, toàn bộ Project cập nhật theo | Đã làm |
| Khi xóa Stage đang có Task, hệ thống không cho xóa | Đã làm |
| Cleanup Stage trùng, map lại Task, xóa duplicate | Đã làm |

## Lưu ý

- Đặc tả BA_DEV ghi hướng global Stage không cần ghi `project_ids`, nhưng yêu cầu triển khai thực tế đã chốt là vẫn add Project vào `project.task.type.project_ids`.
- Các tính năng cũ của module như tạo Project từ CRM, checklist, người kiểm tra, email và cron vẫn còn trong code, nhưng không thuộc phạm vi nghiệm thu chính của Phần A.
- Sau khi cập nhật code hoặc XML, cần nâng cấp module `dcg_project_customize`.

Lệnh tham khảo:

```powershell
E:\DM-Group\doimoi-master\.venv\Scripts\python.exe E:\DM-Group\odoo19\odoo-bin server -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_customize --http-port=8070
```
