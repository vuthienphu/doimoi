# Quy trình kiểm thử `dcg_project_lessons`

Tài liệu này dùng để kiểm thử module **Bài học kinh nghiệm của dự án** sau khi cài đặt hoặc nâng cấp trên Odoo 19.

## 1. Điều kiện trước khi kiểm thử

- Odoo đang chạy, ví dụ `http://localhost:8070`.
- Database đã cài module `project`.
- Module `dcg_project_lessons` đã được cài đặt hoặc nâng cấp.
- Có ít nhất 3 user kiểm thử:
  - Người dùng Nhân viên thuộc nhóm `Bài học kinh nghiệm - Nhân viên`.
  - Người dùng PM thuộc nhóm `Bài học kinh nghiệm - Quản lý dự án`.
  - Người dùng Giám đốc hoặc Quản trị hệ thống.
- Có Project, Task và Milestone để liên kết lesson.

## 2. Nâng cấp module

Thao tác trên giao diện:

1. Vào `Ứng dụng`.
2. Tìm `DCG - Bài học kinh nghiệm dự án`.
3. Bấm `Nâng cấp`.
4. Tải lại trình duyệt bằng `Ctrl + F5`.

Lệnh tham khảo:

```powershell
powershell -ExecutionPolicy Bypass -File E:\DM-Group\doimoi\run_odoo19.ps1 -c E:/DM-Group/doimoi/odoo.conf -d Odoo19CRM -u dcg_project_lessons --stop-after-init --no-http
```

## 3. TC-LESSON-001: Menu Bài học kinh nghiệm

Bước thực hiện:

1. Đăng nhập bằng user có quyền Project.
2. Vào app `Project`.
3. Kiểm tra menu `Bài học kinh nghiệm`.
4. Mở menu này.

Kết quả mong đợi:

- Menu `Dự án > Bài học kinh nghiệm` hiển thị.
- Màn hình mở được danh sách `project.lesson`.
- View mặc định hiển thị Kanban group theo trạng thái.
- Không có lỗi quyền hoặc lỗi view.

## 4. TC-LESSON-002: Tạo Lesson từ menu

Bước thực hiện:

1. Vào `Dự án > Bài học kinh nghiệm`.
2. Bấm `New`.
3. Chọn Project.
4. Nhập Title, Category, Priority, Problem.
5. Nhập Cause, Solution, Result, Recommendation.
6. Chọn Tag hoặc tạo tag mới.
7. Upload file đính kèm.
8. Lưu record.

Kết quả mong đợi:

- Tạo lesson thành công.
- `author_id` mặc định là user đang đăng nhập.
- `date` mặc định là ngày hiện tại.
- `state` mặc định là `Nháp`.
- Attachment hiển thị trong tab Attachments.
- Chatter hiển thị ở form.

## 5. TC-LESSON-003: Tạo Lesson từ Project smart button

Bước thực hiện:

1. Mở một Project.
2. Kiểm tra smart button `Bài học kinh nghiệm`.
3. Bấm smart button.
4. Bấm `New`.
5. Tạo lesson mới.

Kết quả mong đợi:

- Smart button hiển thị đúng số lượng lesson.
- Danh sách lesson được filter theo Project đang mở.
- Khi tạo mới, `project_id` được tự điền theo Project.
- Sau khi lưu, số lượng trên smart button cập nhật đúng.

## 6. TC-LESSON-004: Domain Task và Milestone theo Project

Bước thực hiện:

1. Tạo hoặc mở một lesson.
2. Chọn Project A.
3. Mở dropdown `task_id`.
4. Mở dropdown `milestone_id`.
5. Thử chọn Task hoặc Milestone thuộc Project khác bằng thao tác import/RPC nếu có.

Kết quả mong đợi:

- Dropdown Task chỉ hiển thị Task thuộc Project A.
- Dropdown Milestone chỉ hiển thị Milestone thuộc Project A.
- Nếu cố lưu Task/Milestone khác Project, hệ thống báo lỗi validation.

## 7. TC-LESSON-005: Smart button trên Task

Bước thực hiện:

1. Tạo Lesson liên kết với một Task.
2. Mở form Task đó.
3. Kiểm tra smart button `Lessons`.
4. Bấm smart button.

Kết quả mong đợi:

- Smart button `Lessons` hiển thị đúng số lượng.
- Khi bấm vào, danh sách lesson được filter theo `task_id`.
- Tạo lesson từ màn này tự điền Project và Task.

## 8. TC-LESSON-006: Smart button trên Milestone

Bước thực hiện:

1. Tạo Lesson liên kết với một Milestone.
2. Mở form Milestone đó.
3. Kiểm tra smart button `Lessons`.
4. Bấm smart button.

Kết quả mong đợi:

- Smart button `Lessons` hiển thị đúng số lượng.
- Khi bấm vào, danh sách lesson được filter theo `milestone_id`.
- Tạo lesson từ màn này tự điền Project và Milestone.

## 9. TC-LESSON-007: State machine

Bước thực hiện:

1. Đăng nhập bằng PM.
2. Mở một bài học ở trạng thái Nháp.
3. Bấm `Confirm`.
4. Bấm `Archive`.
5. Bấm `Unarchive`.

Kết quả mong đợi:

- Nháp chuyển sang Đã xác nhận.
- Đã xác nhận chuyển sang Đã lưu trữ.
- Đã lưu trữ chuyển lại Nháp khi bấm Khôi phục.
- Chatter ghi nhận thay đổi state.
- Employee không thấy hoặc không dùng được các action PM.

## 10. TC-LESSON-008: Không xóa lesson chưa archived

Bước thực hiện:

1. Mở bài học ở trạng thái Nháp hoặc Đã xác nhận.
2. Thử xóa record.
3. Chuyển bài học sang Đã lưu trữ.
4. Thử xóa lại bằng Director hoặc System Admin.

Kết quả mong đợi:

- Bài học Nháp/Đã xác nhận không xóa được.
- Hệ thống báo chỉ bài học Đã lưu trữ mới được xóa.
- Giám đốc/Quản trị hệ thống xóa được bài học Đã lưu trữ.

## 11. TC-LESSON-009: Search, filter, group

Bước thực hiện:

1. Tạo dữ liệu lesson với nhiều Category, Priority, State, Project, Author, Tag, Date.
2. Mở `Dự án > Bài học kinh nghiệm`.
3. Thử từng filter và group by.

Kết quả mong đợi:

- Tìm kiếm theo Title hoạt động.
- Tìm kiếm theo Module hoạt động.
- Lọc theo Category hoạt động.
- Lọc theo Tag hoạt động.
- Lọc theo Project hoạt động.
- Lọc theo Author hoạt động.
- Lọc theo Date hoạt động.
- Lọc theo State hoạt động.
- Lọc theo Priority hoạt động.
- Group by Category, Project, State, Priority, Author hoạt động.

## 12. TC-LESSON-010: Pivot và Graph

Bước thực hiện:

1. Tạo nhiều lesson thuộc nhiều Category và Project.
2. Chuyển sang Pivot view.
3. Chuyển sang Graph view.

Kết quả mong đợi:

- Pivot hiển thị lesson theo Category và Project.
- Graph bar chart hiển thị số lesson theo Category.
- Không có lỗi view/report.

## 13. TC-LESSON-011: Cảnh báo khi đóng dự án còn bài học Nháp

Bước thực hiện:

1. Tạo dự án có ít nhất một bài học ở trạng thái Nháp.
2. Mở Project.
3. Archive Project.
4. Trong trình cảnh báo, bấm `Hủy để xem lại`.
5. Lặp lại thao tác archive Project.
6. Trong wizard, bấm `Tiep tuc`.

Kết quả mong đợi:

- Khi dự án còn bài học Nháp, trình cảnh báo xuất hiện.
- Bấm `Hủy để xem lại` mở danh sách bài học Nháp của dự án.
- Bấm `Tiep tuc` vẫn archive Project.
- Nếu dự án không còn bài học Nháp, lưu trữ dự án không hiện cảnh báo.

## 14. TC-LESSON-012: Phân quyền Employee

Bước thực hiện:

1. Đăng nhập bằng user Employee.
2. Tạo một lesson mới.
3. Sửa bài học do chính mình tạo khi còn Nháp.
4. Mở lesson do user khác tạo.
5. Thử sửa lesson do user khác tạo.

Kết quả mong đợi:

- Employee tạo lesson được.
- Nhân viên sửa được bài học Nháp do mình tạo.
- Employee không sửa được lesson của người khác.
- Employee không confirm/archive/unarchive được lesson.

## 15. TC-LESSON-013: Phân quyền PM

Bước thực hiện:

1. Đăng nhập bằng PM.
2. Mở lesson thuộc Project do PM quản lý hoặc theo dõi.
3. Sửa lesson.
4. Confirm lesson.
5. Archive lesson.

Kết quả mong đợi:

- PM đọc và sửa được lesson thuộc project của mình.
- PM xác nhận được bài học Nháp.
- PM archive được lesson.
- PM không xóa được lesson nếu không thuộc Director/System Admin.

## 16. TC-LESSON-014: Phân quyền Director/System Admin

Bước thực hiện:

1. Đăng nhập bằng Director hoặc System Admin.
2. Mở danh sách toàn bộ Bài học kinh nghiệm.
3. Sửa lesson bất kỳ.
4. Archive lesson bất kỳ.
5. Xóa bài học Đã lưu trữ.

Kết quả mong đợi:

- Director/System Admin có quyền trên toàn bộ lesson.
- Xóa được bài học Đã lưu trữ.
- Không bị giới hạn bởi Project.

## 17. Danh sách nghiệm thu nhanh

- [ ] Module nâng cấp không lỗi.
- [ ] Menu `Dự án > Bài học kinh nghiệm` hiển thị.
- [ ] Tạo lesson từ menu hoạt động.
- [ ] Tạo lesson từ Project smart button hoạt động.
- [ ] Project smart button hiển thị đúng count.
- [ ] Task smart button hiển thị đúng count.
- [ ] Milestone smart button hiển thị đúng count.
- [ ] Domain `task_id` lọc đúng theo `project_id`.
- [ ] Domain `milestone_id` lọc đúng theo `project_id`.
- [ ] Validation chặn Task/Milestone khác Project.
- [ ] Upload attachment hoạt động.
- [ ] Tag quick-create hoạt động.
- [ ] Trạng thái Nháp -> Đã xác nhận -> Đã lưu trữ hoạt động.
- [ ] Chatter ghi log khi đổi state.
- [ ] Không xóa được bài học chưa Đã lưu trữ.
- [ ] Kanban group theo state hoạt động.
- [ ] List/Form/Pivot/Graph hoạt động.
- [ ] 9 tiêu chí search/filter hoạt động.
- [ ] Cảnh báo khi lưu trữ dự án còn bài học Nháp hoạt động.
- [ ] Employee không sửa được lesson của người khác.
- [ ] PM confirm/archive được lesson thuộc project của mình.
- [ ] Director/System Admin toàn quyền.

## 18. Ghi chú phạm vi

- Module chưa thêm tab riêng trên Task/Milestone, hiện dùng smart button theo đặc tả cho phép.
- Cảnh báo đóng Project xử lý khi người dùng gọi action archive từ UI. Nếu custom code gọi trực tiếp `write({'active': False})`, Odoo không thể trả wizard cho giao diện.
