# Quy trình kiểm thử `dcg_project_dashboard`

Tài liệu này dùng để kiểm thử **Phần B: Dashboard quản trị dự án**.

## 1. Điều kiện trước khi kiểm thử

- Odoo đang chạy.
- Đã cài hoặc nâng cấp `dcg_project_customize`.
- Đã cài hoặc nâng cấp `dcg_project_dashboard`.
- User kiểm thử thuộc nhóm Project Manager hoặc nhóm `Giám đốc Dashboard Dự án`.
- Database có Project, Task, Stage và người phụ trách để kiểm thử số liệu.

## 2. Nâng cấp module

```powershell
E:\DM-Group\doimoi-master\.venv\Scripts\python.exe E:\DM-Group\odoo19\odoo-bin server -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_dashboard --http-port=8070
```

Sau khi nâng cấp, tải lại trình duyệt bằng `Ctrl + F5`.

## 3. TC-DASH-001: Menu Dashboard

Bước thực hiện:

1. Đăng nhập bằng user Project Manager.
2. Mở màn hình Apps/Home của Odoo.
3. Kiểm tra app `Dashboard Dự án` có icon riêng.
4. Bấm vào app `Dashboard Dự án`.

Kết quả mong đợi:

- App `Dashboard Dự án` hiển thị ngoài màn hình chính Odoo.
- App có icon riêng của module `dcg_project_dashboard`.
- Màn hình Dashboard mở được.
- Không có lỗi asset JS/XML/CSS.
- URL và giao diện không phải app `Báo cáo tổng quan` mặc định của Odoo.
- Không dùng màn `/odoo/dashboards?...` để kiểm thử module này.

Lưu ý:

- App `Báo cáo tổng quan` là dashboard mặc định của Odoo từ module `spreadsheet_dashboard`. Nếu màn hình có tiêu đề `Báo cáo tổng quan`, thanh tìm kiếm/report của Odoo và các biểu đồ mặc định như `Nhiệm vụ theo giai đoạn`, đó không phải module `dcg_project_dashboard`.
- Dashboard của module này là app `Dashboard Dự án`, có tiêu đề `Dashboard`, bộ lọc riêng gồm Khoảng thời gian, Kiểu thống kê, Dự án, Khách hàng, PM, Nhân sự và Stage.

## 4. TC-DASH-001B: Bỏ Dashboard mặc định của Odoo

Bước thực hiện:

1. Vào `Apps`.
2. Tìm module `Spreadsheet dashboard`.
3. Nếu không dùng dashboard mặc định của Odoo, bấm `Uninstall`.
4. Nếu chỉ muốn ẩn menu, bật Developer mode rồi vào `Settings > Technical > User Interface > Menu Items`.
5. Tìm XML ID `spreadsheet_dashboard.spreadsheet_dashboard_menu_root`.
6. Archive menu hoặc giới hạn nhóm quyền.

Kết quả mong đợi:

- App `Báo cáo tổng quan` / `Dashboards` mặc định không còn hiển thị với user kiểm thử.
- App `Dashboard Dự án` của module `dcg_project_dashboard` vẫn hiển thị và mở được.

## 5. TC-DASH-002: Bộ lọc hiển thị đầy đủ

Bước thực hiện:

1. Mở Dashboard.
2. Kiểm tra thanh lọc phía trên.

Kết quả mong đợi:

- Có bộ lọc khoảng thời gian.
- Có Từ ngày, Đến ngày.
- Có Kiểu thống kê.
- Có Dự án, Khách hàng, PM, Nhân sự, Stage dưới dạng chọn tag/chip gọn.
- Có khu `Thông tin cơ bản` và `Nhân sự & khách hàng`.
- Danh sách Stage chỉ hiển thị 5 Stage chuẩn: `Cần làm`, `Đang làm`, `Chuyển test`, `Hoàn thành`, `Đã đưa lên Live`.
- Không hiển thị personal stage mặc định của Odoo như `Inbox`, `Today`, `This Week`, `Later`, `Done`, `Cancelled`.

## 6. TC-DASH-003: KPI tổng hợp

Bước thực hiện:

1. Mở Dashboard.
2. Thay đổi khoảng thời gian.
3. Chọn một hoặc nhiều Project.

Kết quả mong đợi:

- KPI thay đổi theo bộ lọc.
- Có các chỉ số Tổng Project, Project đang triển khai, Project hoàn thành, Project quá hạn, Tổng Task, Task quá hạn, Task hôm nay, Task tháng này.
- KPI có icon, màu nhấn và nền thẻ riêng.
- Có dải chỉ số Task theo 5 Stage chuẩn: `Cần làm`, `Đang làm`, `Chuyển test`, `Hoàn thành`, `Đã đưa lên Live`.

## 7. TC-DASH-004: Stage động

Bước thực hiện:

1. Tạo thêm Stage mới trong `Dự án > Cấu hình > Giai đoạn công việc`.
2. Tải lại Dashboard.
3. Mở bộ lọc Stage và biểu đồ phân bố Task theo Stage.

Kết quả mong đợi:

- Stage mới xuất hiện trong bộ lọc Stage.
- Nếu có Task ở Stage mới, biểu đồ phân bố Task theo Stage hiển thị Stage đó.
- Không cần sửa mã nguồn frontend.

## 8. TC-DASH-004B: Biểu đồ quản trị

Bước thực hiện:

1. Mở Dashboard.
2. Kiểm tra widget `Phân bố Task theo Stage`.
3. Kiểm tra widget `Xu hướng Task`.

Kết quả mong đợi:

- `Phân bố Task theo Stage` hiển thị dạng donut chart, có legend, số lượng và phần trăm.
- Donut chart ưu tiên 5 Stage chuẩn của dự án.
- `Xu hướng Task` hiển thị line chart với 3 đường: Tạo, Hoàn thành, Quá hạn.
- Line chart có trục X/Y cơ bản, legend rõ ràng và không bị trống khung khi không có dữ liệu.

## 9. TC-DASH-005: Bảng tiến độ Project

Bước thực hiện:

1. Mở Dashboard.
2. Kiểm tra bảng tiến độ Project.
3. Bấm các header `Dự án`, `Tiến độ`, `Done/Tổng`, `Deadline`, `PM`.

Kết quả mong đợi:

- Hiển thị tên Project, PM, Deadline, Done/Tổng Task, Progress và số Task theo từng Stage.
- Progress được tính theo công thức `Task Done / Tổng Task * 100`.
- Cột Stage luôn bung đủ 5 Stage chuẩn.
- Bấm header lần đầu sắp xếp tăng dần, bấm lại đảo chiều giảm dần.
- Header có icon sort thể hiện trạng thái sắp xếp.

## 10. TC-DASH-006: Workload nhân sự

Bước thực hiện:

1. Tạo Task có người được giao.
2. Đặt Task ở các Stage `Đang làm`, `Chuyển test`, `Hoàn thành`.
3. Mở Dashboard và kiểm tra Workload.
4. Bấm các header trong bảng Workload.

Kết quả mong đợi:

- Workload hiển thị theo từng nhân sự.
- Có số Task đang làm, chuyển test, hoàn thành trong tuần, chưa xong, quá hạn, tổng Task và tỷ lệ hoàn thành.
- Chỉ hiển thị Top 10 nhân sự theo tổng Task.
- Cột Nhân sự có avatar tròn nhỏ.
- Cột Quá hạn hiển thị badge.
- Cột `%` hiển thị số phần trăm và mini progress bar.
- Có thể sắp xếp theo Nhân sự, Đang làm, Test, Done tuần, Quá hạn, Tổng, `%`.

## 11. TC-DASH-007: Danh sách Task đặc biệt

Bước thực hiện:

1. Tạo Task quá hạn.
2. Tạo Task deadline trong 3 ngày tới.
3. Tạo Task ở Stage `Chuyển test`.
4. Tạo Task ở Stage `Hoàn thành` nhưng chưa `Đã đưa lên Live`.
5. Mở Dashboard.

Kết quả mong đợi:

- Task quá hạn xuất hiện trong danh sách Task quá hạn.
- Task deadline trong 3 ngày tới xuất hiện trong Task sắp đến hạn.
- Task Stage `Chuyển test` xuất hiện trong Task chuyển test.
- Task Stage `Hoàn thành` chưa Live xuất hiện trong Task chưa đưa Live.
- `Task quá hạn` và `Task sắp đến hạn` chỉ hiển thị Top 10 dòng.
- Cột Người thực hiện có avatar tròn nhỏ.
- Cột Trễ hiển thị badge: đỏ cho quá hạn, vàng/cam cho sắp đến hạn.
- Cột Task và Dự án giới hạn tối đa 2 dòng, hover hiển thị tooltip đầy đủ.

## 12. TC-DASH-008: API JSON

Kiểm tra các route trả dữ liệu:

- `/dashboard/summary`
- `/dashboard/project`
- `/dashboard/task_stage`
- `/dashboard/task_trend`
- `/dashboard/workload`
- `/dashboard/project_progress`
- `/dashboard/overdue`
- `/dashboard/testing`
- `/dashboard/not_live`
- `/dashboard/upcoming`

Kết quả mong đợi:

- API trả JSON.
- API tôn trọng filter truyền vào từ frontend.
- API không trả lỗi quyền truy cập với user hợp lệ.

## 13. Danh sách nghiệm thu nhanh

- [ ] App `Dashboard Dự án` hiển thị ngoài màn hình chính.
- [ ] App có icon riêng.
- [ ] App `Báo cáo tổng quan` mặc định của Odoo đã được gỡ hoặc ẩn nếu không dùng.
- [ ] Dashboard mở không lỗi.
- [ ] Bộ lọc thời gian hoạt động.
- [ ] Bộ lọc nhiều lựa chọn hiển thị dạng tag/chip.
- [ ] Bộ lọc Stage chỉ có 5 Stage chuẩn, không lẫn personal stage của Odoo.
- [ ] KPI cập nhật theo filter.
- [ ] KPI có icon, màu nhấn, spacing đồng đều.
- [ ] Có dải chỉ số Task theo 5 Stage chuẩn.
- [ ] Phân bố Task theo Stage cập nhật theo dữ liệu.
- [ ] Donut chart có legend và phần trăm.
- [ ] Line chart xu hướng có 3 đường Tạo/Hoàn thành/Quá hạn.
- [ ] Bảng tiến độ Project đúng công thức.
- [ ] Bảng tiến độ Project có sort theo cột.
- [ ] Bảng tiến độ Project bung đủ 5 Stage chuẩn.
- [ ] Workload nhân sự đúng số liệu.
- [ ] Workload nhân sự có avatar, badge quá hạn, mini progress bar và sort theo cột.
- [ ] Danh sách Task quá hạn đúng.
- [ ] Danh sách Task quá hạn có badge trễ, avatar và giới hạn Top 10.
- [ ] Danh sách Task sắp đến hạn đúng.
- [ ] Danh sách Task sắp đến hạn có badge cảnh báo, avatar và giới hạn Top 10.
- [ ] Danh sách Task chuyển test đúng.
- [ ] Danh sách Task chưa đưa Live đúng.
