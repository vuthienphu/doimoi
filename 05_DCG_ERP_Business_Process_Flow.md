# 05_DCG_ERP_Business_Process_Flow

Version: 1.0

# Mục đích

Tài liệu mô tả chi tiết luồng nghiệp vụ của từng phân hệ: - Ai thực
hiện - Truy cập menu nào - Thao tác gì - Kết quả đầu ra - Module kế tiếp

------------------------------------------------------------------------

# 1. Master Data

## Thực hiện bởi

-   System Administrator
-   HR
-   PMO

## Menu

Settings → Master Data

## Quy trình

1.  Khai báo Company
2.  Khai báo Department
3.  Khai báo Employee
4.  Khai báo Customer Group
5.  Khai báo Industry
6.  Khai báo Project Type
7.  Khai báo Contract Type
8.  Khai báo Currency
9.  Khai báo UoM

## Đầu ra

Toàn bộ dữ liệu dùng chung cho hệ thống.

Module tiếp theo: Approval Matrix

------------------------------------------------------------------------

# 2. Approval Matrix

## Thực hiện

Administrator

## Menu

Configuration → Approval Matrix

## Quy trình

1.  Tạo Approval Flow
2.  Chọn Module áp dụng
3.  Khai báo điều kiện
4.  Thêm cấp duyệt
5.  Kích hoạt

Được sử dụng bởi:

-   CRM
-   Contract
-   Business Trip
-   Finance
-   Document

------------------------------------------------------------------------

# 3. CRM Presales

## Thực hiện

Sales

## Menu

CRM → Presales

## Luồng

Lead ↓ Opportunity ↓ Meeting ↓ Proposal ↓ Approval ↓ Contract

### Công việc

-   Tạo Lead
-   Chăm sóc
-   Chuyển Opportunity
-   Báo giá
-   Trình duyệt

Đầu ra

Contract Draft

Module tiếp: Contract Management

------------------------------------------------------------------------

# 4. Contract Management

## Thực hiện

Sales Legal Director

## Menu

Contract

## Luồng

Proposal ↓ Contract Draft ↓ Approval ↓ Signed ↓ Active ↓ Project

### Công việc

-   Soạn hợp đồng
-   Phụ lục
-   Gia hạn
-   Thanh lý

Đầu ra

Project

------------------------------------------------------------------------

# 5. Project Delivery

## Thực hiện

PM

## Menu

Project

## Luồng

Create Project ↓ Milestone ↓ Task ↓ Assign Member ↓ Execute ↓ Acceptance
↓ Warranty

### Thành viên

PM

BA

Developer

QA

Customer

------------------------------------------------------------------------

# 6. Resource Planning

## Thực hiện

PMO

## Menu

Resource Planning

## Luồng

Capacity ↓ Resource Request ↓ Allocation ↓ Confirm

Đầu ra

Project Member

------------------------------------------------------------------------

# 7. Timesheet

## Thực hiện

Developer BA QA

## Menu

Timesheet

## Luồng

Daily Timesheet ↓ Submit ↓ Manager Approval ↓ Lock Period

Đầu ra

Labor Cost

------------------------------------------------------------------------

# 8. Project Finance

## Thực hiện

Finance

## Menu

Project Finance

## Luồng

Timesheet + Expense + Invoice ↓ Revenue ↓ Cost ↓ Margin

------------------------------------------------------------------------

# 9. Business Trip

## Thực hiện

Employee

## Menu

Business Trip

## Luồng

Request ↓ Approval ↓ Trip ↓ Expense ↓ Settlement

------------------------------------------------------------------------

# 10. Helpdesk Warranty

## Thực hiện

Support

## Menu

Warranty

## Luồng

Ticket ↓ Assign ↓ Analysis ↓ Fix ↓ Customer Confirm ↓ Close

------------------------------------------------------------------------

# 11. Document Management

## Thực hiện

Tất cả người dùng

## Menu

Documents

## Luồng

Create Folder ↓ Upload ↓ Review ↓ Approval ↓ Publish ↓ Archive

------------------------------------------------------------------------

# 12. HR Resource

## Thực hiện

HR PMO

## Menu

HR Resource

## Luồng

Employee ↓ Role ↓ Skill ↓ Certificate ↓ KPI

------------------------------------------------------------------------

# 13. Asset IT

## Thực hiện

IT

## Menu

Asset

## Luồng

Purchase ↓ Register ↓ Assign ↓ Maintenance ↓ Return ↓ Retire

------------------------------------------------------------------------

# 14. Dashboard KPI

## Thực hiện

CEO Manager

## Menu

Dashboard

## Dữ liệu lấy từ

-   CRM
-   Contract
-   Project
-   Resource
-   Timesheet
-   Finance
-   Business Trip
-   Warranty
-   Document
-   HR Resource
-   Asset

Dashboard chỉ đọc dữ liệu, không cập nhật nghiệp vụ.

------------------------------------------------------------------------

# Quy trình tổng thể

Lead → Opportunity → Proposal → Approval → Contract → Project → Resource
Planning → Timesheet → Finance → Warranty → Dashboard
