# Dashboard KPI - Hướng dẫn cấu hình và sử dụng

**Module:** `dcg_dashboard_kpi`
**Phiên bản:** Odoo 18 Community

---

# 1. Mục đích

Dashboard KPI là màn hình tổng hợp dữ liệu từ toàn bộ hệ thống DCG ERP nhằm giúp Ban lãnh đạo và các cấp quản lý theo dõi tình hình hoạt động theo thời gian thực.

Dashboard **không lưu dữ liệu**, chỉ đọc dữ liệu từ các module nghiệp vụ.

---

# 2. Kiến trúc Dashboard

```text
CRM
Contract
Project
Resource Planning
Timesheet
Finance
Business Trip
Warranty
Document
HR Resource
Asset IT
        │
        ▼
 Dashboard Service
        │
        ▼
 Dashboard KPI
```

Dashboard chỉ hiển thị dữ liệu theo quyền của người dùng.

---

# 3. Điều kiện sử dụng

Để Dashboard hoạt động đầy đủ cần:

* Cài đặt module `dcg_dashboard_kpi`
* Cài đặt các module nghiệp vụ liên quan
* Có dữ liệu thực tế
* Có quyền Dashboard User hoặc Dashboard Manager

---

# 4. Phân quyền

## Dashboard User

* Xem Dashboard theo quyền
* Drill-down dữ liệu
* Export PDF / Excel

Không được:

* Chỉnh sửa Widget
* Thay đổi Dashboard

---

## Dashboard Manager

Ngoài quyền User còn có:

* Cấu hình Dashboard
* Tạo Dashboard mới
* Thêm Widget
* Thay đổi Layout

---

## Administrator

Toàn quyền.

---

# 5. Menu

```
Dashboard

├── Executive Dashboard
├── Sales Dashboard
├── Project Dashboard
├── Finance Dashboard
├── Resource Dashboard
├── Support Dashboard
├── Asset Dashboard
└── Dashboard Configuration
```

---

# 6. Dashboard Configuration

Menu

```
Dashboard

↓

Configuration
```

Bao gồm

```
Dashboard

Dashboard Group

Widget

Chart

KPI

Permission

Refresh Policy
```

---

# 7. Dashboard

Một Dashboard gồm

```
Tên

Mã

Mô tả

Loại

Layout

Company

Active
```

Ví dụ

```
Executive Dashboard
```

---

# 8. Widget

Một Dashboard có nhiều Widget.

Ví dụ

```
Revenue

Profit

Margin

Project

Timesheet

Resource

Ticket
```

---

## Thuộc tính Widget

* Tên
* Loại
* Dashboard
* Sequence
* Kích thước
* Màu
* Icon
* RPC Service
* Drill Down Action

---

# 9. Loại Widget

## KPI Card

Ví dụ

```
Revenue

15 tỷ
```

---

## Table

Ví dụ

```
Top Project
```

---

## Line Chart

```
Revenue Trend
```

---

## Bar Chart

```
Project Progress
```

---

## Pie Chart

```
Project Status
```

---

## Gauge

```
Utilization
```

---

## Progress

```
Milestone
```

---

## Calendar

```
Upcoming Deadline
```

---

# 10. Layout

Dashboard chia thành Grid.

Ví dụ

```
4 Card

↓

2 Chart

↓

2 Table

↓

Alert
```

Mỗi Widget khai báo:

* Row
* Column
* Width
* Height

---

# 11. Bộ lọc chung

Dashboard sử dụng Filter chung.

```
Company

Branch

Department

Project

Customer

Employee

Period
```

Ngoài ra

```
Today

This Week

This Month

Quarter

Year
```

---

# 12. Dashboard Executive

Nguồn dữ liệu

```
CRM

Contract

Project

Finance

Resource

Warranty
```

Widget

* Revenue
* Profit
* Margin
* Active Project
* Resource Utilization
* Open Ticket
* Contract Expiry
* Cashflow

---

# 13. Dashboard Sales

Nguồn

```
CRM
Contract
```

Widget

* Lead
* Opportunity
* Proposal
* Win Rate
* Contract

---

# 14. Dashboard Project

Nguồn

```
Project Delivery
```

Widget

* Project Status
* Milestone
* Progress
* Delay
* Issue
* Risk

---

# 15. Dashboard Resource

Nguồn

```
Resource Planning

HR Resource

Timesheet
```

Widget

* Allocation
* Capacity
* Utilization
* Available Resource
* Over Allocation

---

# 16. Dashboard Finance

Nguồn

```
Project Finance
```

Widget

* Revenue
* Cost
* Margin
* Invoice
* Payment
* Cashflow

---

# 17. Dashboard Support

Nguồn

```
Warranty
```

Widget

* Open Ticket
* SLA
* Critical
* Average Response
* Average Resolve

---

# 18. Dashboard Asset

Nguồn

```
Asset IT
```

Widget

* Asset
* Maintenance
* Warranty
* License
* Depreciation

---

# 19. Dashboard Refresh

Có hai chế độ.

## Manual

Nhấn Refresh.

---

## Auto

Ví dụ

```
5 phút

10 phút

15 phút

30 phút
```

Khuyến nghị

```
5 phút
```

---

# 20. Drill Down

Ví dụ

```
Revenue Card

↓

Invoice List

↓

Invoice Form
```

Hoặc

```
Project

↓

Project List

↓

Project Form
```

---

# 21. Dashboard Service

Dashboard gọi

```
dashboard_service.py
```

Ví dụ

```
get_executive_dashboard()

get_finance_dashboard()

get_project_dashboard()
```

Backend trả JSON.

---

# 22. Widget Service

Không Query trực tiếp trong OWL.

Luôn

```
OWL

↓

RPC

↓

Python Service

↓

ORM
```

---

# 23. Dashboard Cache

Khuyến nghị

```
5 phút
```

Cache theo

* Company
* User
* Period
* Department

---

# 24. Dashboard Security

Dashboard luôn tuân theo Record Rule.

Ví dụ

PM chỉ xem

```
Project của mình
```

Sales chỉ xem

```
Lead của mình
```

CEO

```
Toàn công ty
```

---

# 25. Dashboard Theme

Khuyến nghị

```
Primary

Success

Warning

Danger
```

Không dùng quá nhiều màu.

---

# 26. Export

Dashboard hỗ trợ

* PDF
* Excel
* CSV

---

# 27. Responsive

Desktop

```
4 Widget / Row
```

Tablet

```
2 Widget
```

Mobile

```
1 Widget
```

---

# 28. Best Practice

* Không đặt quá 15 Widget trên một Dashboard.
* KPI tính ở Backend, không tính ở JavaScript.
* Widget chỉ hiển thị dữ liệu cần thiết.
* Mỗi Widget chỉ thực hiện một mục tiêu nghiệp vụ.
* Sử dụng Drill-down thay vì hiển thị quá nhiều chi tiết.
* Cache dữ liệu để giảm tải truy vấn.
* Mọi Dashboard phải tuân thủ phân quyền của Odoo.

---

# 29. Quy trình hoạt động

```
User Login

↓

Load Dashboard

↓

Load Filter

↓

RPC Dashboard Service

↓

Query ORM

↓

Return JSON

↓

Render Widget

↓

Drill Down (nếu người dùng thao tác)
```

---

# 30. Checklist triển khai

* [ ] Cài đặt module `dcg_dashboard_kpi`
* [ ] Cấu hình quyền Dashboard
* [ ] Tạo Dashboard
* [ ] Tạo Widget
* [ ] Cấu hình Filter
* [ ] Cấu hình Drill-down
* [ ] Kiểm tra Record Rule
* [ ] Kiểm tra hiệu năng
* [ ] Kiểm tra Responsive
* [ ] Kiểm tra Export PDF/Excel
* [ ] Kiểm tra Dashboard theo từng vai trò (CEO, Sales, PM, Finance, HR, Support, IT)

---

# Kết luận

Dashboard KPI là lớp trình bày (Presentation Layer) của hệ thống DCG ERP. Toàn bộ dữ liệu đều được lấy từ các module nghiệp vụ thông qua Service Layer, đảm bảo tuân thủ phân quyền Odoo và hỗ trợ Ban lãnh đạo theo dõi hoạt động doanh nghiệp theo thời gian thực.
