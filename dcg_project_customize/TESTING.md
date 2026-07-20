# Quy trình kiểm thử `dcg_project_customize`

Tài liệu này dùng để kiểm thử **Phần A: Chuẩn hóa Stage của Dự án** sau khi cài đặt hoặc nâng cấp module `dcg_project_customize` trên Odoo 19.

## 1. Điều kiện trước khi kiểm thử

- Odoo đang chạy, ví dụ `http://localhost:8070`.
- Database đã cài module `project`.
- Module `dcg_project_customize` đã được cài đặt hoặc nâng cấp.
- Người dùng kiểm thử có quyền Quản lý Dự án hoặc quyền cấu hình Stage.

## 2. Nâng cấp module

Thao tác trên giao diện:

1. Vào `Ứng dụng`.
2. Tìm `DCG Project Customize`.
3. Bấm `Nâng cấp`.
4. Tải lại trình duyệt bằng `Ctrl + F5`.

Lệnh tham khảo:

```powershell
E:\DM-Group\doimoi-master\.venv\Scripts\python.exe E:\DM-Group\odoo19\odoo-bin server -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_customize --http-port=8070
```

## 3. TC-STAGE-001: Kiểm tra 5 Stage mặc định

Đường dẫn:

```text
Dự án > Cấu hình > Giai đoạn công việc
```

Bước thực hiện:

1. Mở danh sách Stage.
2. Kiểm tra danh sách Stage sau khi nâng cấp module.

Kết quả mong đợi:

- Có đủ 5 Stage:
  - `Cần làm`
  - `Đang làm`
  - `Chuyển test`
  - `Hoàn thành`
  - `Đã đưa lên Live`
- Không còn Stage tên cũ `Đang thực hiện` hoặc `Chờ kiểm tra` nếu các Stage đó là duplicate từ dữ liệu cũ.

## 4. TC-STAGE-002: Kiểm tra cờ nghiệp vụ trên Stage

Bước thực hiện:

1. Mở Stage `Cần làm`.
2. Mở Stage `Đang làm`.
3. Mở Stage `Chuyển test`.
4. Mở Stage `Hoàn thành`.
5. Mở Stage `Đã đưa lên Live`.

Kết quả mong đợi:

| Stage | Kết quả mong đợi |
| --- | --- |
| `Cần làm` | Không tick cờ nghiệp vụ |
| `Đang làm` | Chỉ tick `Đang làm` |
| `Chuyển test` | Chỉ tick `Chuyển test` |
| `Hoàn thành` | Chỉ tick `Hoàn thành` |
| `Đã đưa lên Live` | Chỉ tick `Đã đưa lên Live` |

## 5. TC-STAGE-003: Tạo Project mới dùng được toàn bộ Stage

Bước thực hiện:

1. Vào app `Dự án`.
2. Tạo một Project mới.
3. Mở kanban Công việc của Project vừa tạo.

Kết quả mong đợi:

- Project mới có thể sử dụng toàn bộ Stage đang có trong hệ thống.
- 5 Stage mặc định hiển thị trong kanban Công việc.
- Người dùng không phải thêm Stage thủ công cho Project mới.

## 6. TC-STAGE-004: Tạo Stage mới áp dụng cho toàn bộ Project

Bước thực hiện:

1. Vào `Dự án > Cấu hình > Giai đoạn công việc`.
2. Tạo Stage mới, ví dụ `Khách hàng UAT`.
3. Mở một Project cũ đã tồn tại trước khi tạo Stage.
4. Mở một Project mới tạo sau khi tạo Stage.

Kết quả mong đợi:

- Stage `Khách hàng UAT` dùng được trên tất cả Project.
- Không cần mở từng Project để thêm Stage thủ công.

## 7. TC-STAGE-005: Sửa tên Stage cập nhật đồng bộ

Bước thực hiện:

1. Mở Stage `Khách hàng UAT`.
2. Đổi tên thành `Khách hàng kiểm tra`.
3. Mở nhiều Project khác nhau.

Kết quả mong đợi:

- Các Project đều hiển thị tên Stage mới `Khách hàng kiểm tra`.
- Không phát sinh Stage duplicate chỉ vì đổi tên.

## 8. TC-STAGE-006: Không cho xóa Stage đang được sử dụng

Bước thực hiện:

1. Tạo một Task và gán vào Stage `Đang làm`.
2. Vào cấu hình Stage.
3. Thử xóa Stage `Đang làm`.

Kết quả mong đợi:

- Hệ thống không cho xóa Stage.
- Hiển thị thông báo:

```text
Stage đang được sử dụng.
```

## 9. TC-STAGE-007: Cho phép xóa Stage chưa được sử dụng

Bước thực hiện:

1. Tạo một Stage test mới, ví dụ `Stage tạm`.
2. Đảm bảo không có Task nào dùng Stage này.
3. Xóa Stage `Stage tạm`.

Kết quả mong đợi:

- Stage được xóa thành công.
- Không ảnh hưởng các Stage mặc định.

## 10. TC-STAGE-008: Cleanup Stage trùng từ dữ liệu cũ

Điều kiện dữ liệu:

- Database có Stage cũ hoặc duplicate, ví dụ:
  - `Đang thực hiện`
  - `Chờ kiểm tra`
  - Nhiều bản ghi cùng tên `Đang làm`
  - Nhiều bản ghi cùng tên `Chuyển test`

Bước thực hiện:

1. Nâng cấp module `dcg_project_customize`.
2. Mở danh sách Stage.
3. Kiểm tra Task trước đó đang nằm ở Stage duplicate.

Kết quả mong đợi:

- Stage `Đang thực hiện` được gom về `Đang làm`.
- Stage `Chờ kiểm tra` được gom về `Chuyển test`.
- Task đang ở Stage duplicate được chuyển sang Stage chuẩn tương ứng.
- Stage duplicate không còn tồn tại sau cleanup.
- Việc cleanup không gửi email thông báo đổi Stage hàng loạt.

## 11. Danh sách nghiệm thu Phần A

- [ ] Module nâng cấp không lỗi.
- [ ] Có đúng 5 Stage mặc định theo đặc tả.
- [ ] Cờ nghiệp vụ trên Stage đúng.
- [ ] Tạo Project mới dùng được toàn bộ Stage.
- [ ] Tạo Stage mới áp dụng cho toàn bộ Project.
- [ ] Sửa tên Stage cập nhật đồng bộ.
- [ ] Không xóa được Stage đang có Task.
- [ ] Xóa được Stage chưa có Task.
- [ ] Cleanup Stage trùng map lại Task đúng.
- [ ] Không còn Stage duplicate từ tên cũ `Đang thực hiện`, `Chờ kiểm tra`.

## 12. Ghi chú phạm vi

Tài liệu này chỉ kiểm thử Phần A. Các phần CRM tạo Project, checklist, người kiểm tra, email và cron là tính năng cũ đang còn trong module nhưng không thuộc checklist nghiệm thu chính của Phần A.
