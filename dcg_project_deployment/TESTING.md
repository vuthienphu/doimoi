# Quy trình kiểm thử `dcg_project_deployment`

Tài liệu này dùng để kiểm thử module **Quản lý Thông tin Triển khai** sau khi cài đặt hoặc nâng cấp trên Odoo 19.

## 1. Điều kiện trước khi kiểm thử

- Odoo đang chạy, ví dụ `http://localhost:8070`.
- Database đã cài module `project`.
- Module `dcg_project_deployment` đã được cài đặt hoặc nâng cấp.
- Có ít nhất 3 user kiểm thử:
  - Employee nội bộ không thuộc Project Manager.
  - Project Manager thuộc `project.group_project_manager`.
  - System Admin thuộc `base.group_system`.
- Có ít nhất một Project để tạo account/remote.

## 2. Nâng cấp module

Thao tác trên giao diện:

1. Vào `Ứng dụng`.
2. Tìm `DCG - Thông tin triển khai dự án`.
3. Bấm `Nâng cấp`.
4. Tải lại trình duyệt bằng `Ctrl + F5`.

Lệnh tham khảo:

```powershell
powershell -ExecutionPolicy Bypass -File E:\DM-Group\doimoi\run_odoo19.ps1 -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_deployment --stop-after-init --no-http
```

## 3. TC-DEPLOY-001: Smart button trên Project

Bước thực hiện:

1. Đăng nhập bằng System Admin.
2. Mở một Project.
3. Kiểm tra smart button `Tài khoản`.
4. Kiểm tra smart button `Kết nối máy chủ`.

Kết quả mong đợi:

- `Tài khoản (N)` hiển thị đúng số lượng tài khoản.
- `Kết nối máy chủ (N)` hiển thị đúng số lượng kết nối.
- Bấm smart button mở danh sách được filter theo Project.
- Khi tạo mới từ smart button, `project_id` được tự điền.

## 4. TC-DEPLOY-002: Tạo Project Account bằng System Admin

Bước thực hiện:

1. Đăng nhập bằng System Admin.
2. Vào `Dự án > Triển khai > Tài khoản`.
3. Tạo account mới.
4. Nhập Dự án, Tên tài khoản, Loại tài khoản, Tên đăng nhập, Mật khẩu, Đường dẫn truy cập, Ghi chú.
5. Lưu record.

Kết quả mong đợi:

- Account tạo thành công.
- Password hiển thị bằng widget password.
- Username có nút copy.
- Password có nút copy cho System Admin.
- URL click được.
- Chatter hiển thị trên form.

## 5. TC-DEPLOY-003: PM chỉ đọc account và thấy password masked

Bước thực hiện:

1. Đăng nhập bằng Project Manager.
2. Vào `Dự án > Triển khai > Tài khoản`.
3. Mở account đã tạo.
4. Thử sửa record.

Kết quả mong đợi:

- PM mở được danh sách account.
- PM thấy `password_masked` là `***` nếu account có password.
- PM không thấy password thật.
- PM không tạo/sửa/xóa được account.
- PM không đọc được field `password` qua export/RPC thông thường.

## 6. TC-DEPLOY-004: Employee không truy cập account

Bước thực hiện:

1. Đăng nhập bằng Employee.
2. Kiểm tra menu `Dự án > Triển khai`.
3. Thử truy cập URL trực tiếp với model `project.account`.

Kết quả mong đợi:

- Nhân viên không thấy menu Triển khai.
- Employee không đọc/search/tạo/sửa/xóa được `project.account`.
- Truy cập URL trực tiếp bị lỗi quyền.

## 7. TC-DEPLOY-005: Tạo Remote bằng System Admin

Bước thực hiện:

1. Đăng nhập bằng System Admin.
2. Vào `Dự án > Triển khai > Kết nối máy chủ`.
3. Tạo remote mới.
4. Nhập Dự án, Tên kết nối, Loại máy chủ, Phương thức kết nối.
5. Nhập các field tương ứng.
6. Lưu record.

Kết quả mong đợi:

- Remote tạo thành công.
- Password và Private Key chỉ visible với System Admin.
- Username có nút copy.
- Password có nút copy.
- Private Key có nút copy khi connection type là SSH hoặc VPN.
- Chatter hiển thị trên form.

## 8. TC-DEPLOY-006: Dynamic fields theo connection type

Kiểm tra từng loại connection type:

| Phương thức kết nối | Trường mong đợi |
| --- | --- |
| SSH | host, port, username, password, private_key, path |
| RDP | host, port, username, password |
| UltraViewer | partner_id_field, password |
| AnyDesk | address_field, password |
| TeamViewer | partner_id_field, password |
| Web Server Control Panel | url, username, password |
| Database | host, port, database, username, password |
| FTP | host, port, username, password |
| SFTP | host, port, username, password |
| VPN | host, port, username, password, private_key |

Kết quả mong đợi:

- Field ẩn/hiện đúng theo từng `connection_type`.
- Không có field không liên quan hiển thị sai.

## 9. TC-DEPLOY-007: PM không truy cập remote

Bước thực hiện:

1. Đăng nhập bằng Project Manager.
2. Kiểm tra menu `Dự án > Triển khai`.
3. Kiểm tra menu `Kết nối máy chủ`.
4. Thử truy cập URL trực tiếp với model `project.remote`.

Kết quả mong đợi:

- PM không thấy menu `Kết nối máy chủ`.
- PM không thấy smart button `Remote` trên Project.
- PM không đọc/search/export được `project.remote`.
- Truy cập URL trực tiếp bị lỗi quyền.

## 10. TC-DEPLOY-008: Employee không truy cập remote

Bước thực hiện:

1. Đăng nhập bằng Employee.
2. Thử truy cập URL trực tiếp với model `project.remote`.

Kết quả mong đợi:

- Employee không đọc/search/tạo/sửa/xóa được `project.remote`.
- Truy cập URL trực tiếp bị lỗi quyền.

## 11. TC-DEPLOY-009: Archive account/remote

Bước thực hiện:

1. Đăng nhập bằng System Admin.
2. Mở một account.
3. Bỏ tick `active`.
4. Mở bộ lọc `Đã lưu trữ`.
5. Lặp lại với remote.

Kết quả mong đợi:

- Account/Remote được archive bằng `active=False`.
- Record không bị xóa khỏi DB.
- Bộ lọc `Đã lưu trữ` hiển thị bản ghi đã lưu trữ.
- Smart button vẫn mở được danh sách có context `active_test=False`.

## 12. TC-DEPLOY-010: Search và group

Bước thực hiện:

1. Tạo nhiều account với nhiều Project và Account Type.
2. Tạo nhiều remote với nhiều Project, Server Type và Connection Type.
3. Thử search và group by trên từng màn hình.

Kết quả mong đợi:

- Account search theo name/project/type/username/url hoạt động.
- Account group by Project và Account Type hoạt động.
- Remote search theo name/project/server type/connection type/host/url hoạt động.
- Remote group by Project, Server Type và Connection Type hoạt động.

## 13. Danh sách nghiệm thu nhanh

- [ ] Module nâng cấp không lỗi.
- [ ] Form dự án có smart button `Tài khoản`.
- [ ] Project form có smart button `Remote` chỉ với System Admin.
- [ ] Tạo account bằng System Admin hoạt động.
- [ ] Username account copy được.
- [ ] Password account ẩn mặc định.
- [ ] Password account copy được với System Admin.
- [ ] PM đọc được account list.
- [ ] PM thấy password dạng `***`.
- [ ] PM không tạo/sửa/xóa được account.
- [ ] Employee không truy cập được account.
- [ ] Tạo remote bằng System Admin hoạt động.
- [ ] Remote dynamic fields đúng theo connection type.
- [ ] Username/password/private key remote copy được với System Admin.
- [ ] PM không thấy menu/smart button remote.
- [ ] PM không truy cập được `project.remote` qua URL trực tiếp.
- [ ] Employee không truy cập được `project.remote`.
- [ ] Archive account/remote hoạt động.
- [ ] Search/group account hoạt động.
- [ ] Search/group remote hoạt động.

## 14. Ghi chú bảo mật

- Trước go-live với dữ liệu thật, cần bổ sung mã hóa DB cho `password` và `private_key`.
- Không nhập password thật vào môi trường demo nếu database/log có thể chia sẻ.
- Không export dữ liệu account/remote bằng user không phải System Admin.
