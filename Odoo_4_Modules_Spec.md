# ĐẶC TẢ CHI TIẾT 4 MODULE ODOO

## 1. dcg_custom_crm

### Mục tiêu
Quản lý hoa hồng Sales, khảo sát, demo và tự động tạo Project khi Opportunity Won.

### Models

#### crm.team
- commission_rate (Float, default=2.0)
- Button: Cập nhật toàn bộ hoa hồng

#### crm.team.member
- commission_rate (Float)
- Mặc định lấy từ team

#### crm.lead
Các field:
- commission_rate
- other_ids
- survey_note
- estimate_attachment_ids
- survey_done
- survey_finish_date
- demo_done
- demo_finish_date
- project_id

### Nghiệp vụ
#### Hoa hồng Team
- Không tự đồng bộ khi sửa team
- Chỉ đồng bộ khi bấm button xác nhận

#### Khảo sát
- Hoàn thành khảo sát
- Tiếp tục khảo sát bằng wizard

#### Demo
- Hoàn thành demo
- Tiếp tục demo bằng wizard

#### Tạo Project khi Won
- Kiểm tra project_id
- Nếu chưa có thì tạo Project
- Ghi chatter

### Wizard
Model: crm.survey.wizard

Field:
- type
- content
- date_from
- date_to

### Chatter
- Hoàn thành khảo sát
- Tiếp tục khảo sát
- Hoàn thành demo
- Tiếp tục demo
- Tạo project

---

## 2. dcg_crm_cost

### Mục tiêu
Quản lý chi phí thực tế theo Opportunity.

### Model mới
#### crm.lead.cost

Field:
- lead_id
- cost_type
- name
- date
- amount
- currency_id
- user_id
- attachment_ids

### Kế thừa crm.lead

Field:
- cost_ids
- total_cost
- profit_loss

### Công thức

```python
total_cost = sum(cost_ids.amount)
profit_loss = expected_revenue - total_cost
```

### Giao diện

#### Tab Chi phí
Cột:
- Loại chi phí
- Tên chi phí
- Ngày
- Số tiền
- Người ghi nhận
- Đính kèm

#### Tree Opportunity
Hiển thị:
- Chi phí
- Lãi/Lỗ

Highlight đỏ:
```xml
decoration-danger="profit_loss < 0"
```

### Báo cáo
CRM → Báo cáo → Chi phí

Readonly:
- create=False
- edit=False
- delete=False

---

## 3. dcg_crm_estimation

### Mục tiêu
Ước tính giá trị dự án Presales.

### Model crm.role.cost

Field:
- role
- cost_per_md
- currency_id
- active

Role:
- BA
- Backend
- Frontend
- QA
- DevOps
- UI/UX

*Lưu ý: Hệ thống tự động tạo sẵn dữ liệu mặc định cho 6 vai trò trên với đơn giá 0 VND/MD khi cài đặt module.*

### Model crm.lead.work.estimation

Field:
- module
- name
- description
- priority
- ba_md
- backend_md
- frontend_md
- qa_md
- devops_md
- uiux_md
- total_md

### Compute

```python
total_md = (
    ba_md +
    backend_md +
    frontend_md +
    qa_md +
    devops_md +
    uiux_md
)
```

### Model crm.lead.value.estimation

Field:
- cost_type
- name
- quantity
- unit
- unit_price
- subtotal
- note

### Cost Type
- license
- infra
- partner
- travel
- equipment
- other

### Kế thừa crm.lead

Field:
- work_estimation_ids
- value_estimation_ids
- total_effort
- estimated_human_cost
- estimated_other_cost
- total_estimated_cost
- estimated_profit
- estimated_margin

### Công thức

```python
estimated_profit =
    expected_revenue - total_estimated_cost

estimated_margin =
    estimated_profit / expected_revenue * 100
```

### Giao diện

#### Tab Giá trị ước tính
- Doanh thu dự kiến
- Giá vốn nhân sự
- Giá vốn ngoài nhân sự
- Tổng giá vốn
- Lợi nhuận
- Margin

#### Tab Công việc ước tính
- Module
- Chức năng
- BA
- Backend
- Frontend
- QA
- DevOps
- UI/UX
- Tổng MD

### Menu

CRM
└── Cấu hình
    └── Đơn giá nhân sự

---

## 4. dcg_project_customize

### Mục tiêu
Tự động hóa Project và Task sau khi Opportunity Won.

### Kế thừa project.project

Field:
- lead_id

### Khi tạo Project
- Đồng bộ Opportunity
- Đồng bộ Customer
- Đồng bộ Salesperson
- Gán toàn bộ Stage mặc định

### Kế thừa project.task.type

Field:
- is_processing
- is_test
- is_done
- is_live

### Kế thừa project.task

Field:
- reviewer_ids
- planned_finish_date
- actual_finish_date
- checklist_ids

### Model task.checklist

Field:
- name
- is_done
- task_id

### Email Notification

#### Đang thực hiện
Người nhận:
- create_uid

#### Chờ kiểm tra
Người nhận:
- reviewer_ids

#### Hoàn thành
Người nhận:
- create_uid
- user_ids

### Cron

Tên:
- Daily Task Reminder

Thời gian:
- 08:00 mỗi ngày

### Nhóm nhắc việc

#### Processing
Điều kiện:
- stage.is_processing=True

Người nhận:
- create_uid
- user_ids

#### Testing
Điều kiện:
- stage.is_test=True

Người nhận:
- create_uid
- user_ids
- reviewer_ids

#### Done chưa Live
Điều kiện:
- stage.is_done=True
- stage.is_live=False

Người nhận:
- create_uid
- user_ids

### Cấu trúc Module

```
dcg_project_customize/
├── models/
│   ├── project_project.py
│   ├── project_task.py
│   ├── project_task_type.py
│   └── task_checklist.py
├── views/
├── data/
├── security/
└── __manifest__.py
```

---

---

## 5. dcg_crm_payment

### Mục tiêu
Bổ sung chức năng quản lý thanh toán theo từng Cơ hội (Opportunity), giúp theo dõi tiến độ thanh toán của khách hàng theo hợp đồng, hỗ trợ nhắc thanh toán định kỳ và đánh giá tình trạng công nợ của từng Opportunity.

### Cấu hình Loại thanh toán
**Menu:** CRM > Cấu hình > Loại thanh toán
Cho phép khai báo:
- Tên loại thanh toán.
- Chu kỳ thanh toán (ngày).
- Số ngày nhắc trước kỳ thanh toán.

Ví dụ:
- Hàng tháng: Chu kỳ 30 ngày, Nhắc trước 05 ngày.
- Hàng quý: Chu kỳ 90 ngày, Nhắc trước 10 ngày.
- Hàng năm: Chu kỳ 365 ngày, Nhắc trước 30 ngày.

### Opportunity
Bổ sung thông tin thanh toán:
- Loại thanh toán.
- Ngày thanh toán đầu tiên.
- Ngày thanh toán gần nhất (readonly).
- Lịch sử thanh toán.
- Số tiền đã thanh toán (compute).
- Số tiền còn lại (compute).

Hệ thống tự động tính:
- `total_paid = sum(payment_ids.paid_amount)`
- `remaining_amount = expected_revenue - total_paid`
- `last_payment_date = max(payment_ids.payment_date)`

### Nhắc thanh toán
Hệ thống tự động kiểm tra các Opportunity chưa thanh toán hết giá trị hợp đồng.
Nếu sắp đến kỳ thanh toán theo cấu hình thì gửi email nhắc đến người phụ trách Opportunity (Salesperson).

### Báo cáo lịch sử thanh toán
**Menu:** CRM → Báo cáo → Lịch sử thanh toán
Hiển thị toàn bộ lịch sử thanh toán của các Opportunity.
Mặc định nhóm theo Opportunity.
Màn hình chỉ phục vụ tra cứu, không cho phép tạo, sửa hoặc xóa.

### Cấu trúc Module
```text
dcg_crm_payment/
├── models/
│   ├── crm_payment_type.py
│   ├── crm_lead_payment.py
│   └── crm_lead.py
├── views/
│   ├── crm_payment_type_views.xml
│   ├── crm_lead_views.xml
│   └── crm_lead_payment_views.xml
├── data/
│   ├── cron_data.xml
│   └── mail_template_data.xml
├── security/
│   └── ir.model.access.csv
└── __manifest__.py
```

---

# Tổng kết

| Module | Chức năng |
|----------|----------|
| dcg_custom_crm | Hoa hồng, Survey, Demo, Auto Project |
| dcg_crm_cost | Quản lý chi phí thực tế |
| dcg_crm_estimation | Ước tính giá trị & man-day |
| dcg_project_customize | Quản lý Task, Checklist, Reminder |
| dcg_crm_payment | Quản lý thanh toán, nhắc nợ & công nợ |
