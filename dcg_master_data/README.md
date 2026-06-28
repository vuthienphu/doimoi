# DCG Master Data

Module dữ liệu chủ (master data) dùng chung cho toàn bộ hệ thống nội bộ của
Công ty TNHH Đổi Mới G.R.O.U.P trên nền **Odoo 18 Community**.

## Phạm vi Phase 1

Module gom toàn bộ master data ra khỏi các module nghiệp vụ phase sau, gồm 14 model:

### Nhóm CRM / khách hàng
1. `dcg.customer.industry` – Ngành khách hàng
2. `dcg.customer.source`   – Nguồn khách hàng
3. `dcg.service.catalog`   – Danh mục dịch vụ

### Nhóm hợp đồng / delivery
4. `dcg.contract.type`            – Loại hợp đồng
5. `dcg.contract.appendix.type`   – Loại phụ lục
6. `dcg.acceptance.type`          – Loại nghiệm thu

### Nhóm helpdesk / support
7. `dcg.ticket.type`     – Loại ticket
8. `dcg.ticket.severity` – Mức độ nghiêm trọng
9. `dcg.ticket.priority` – Mức ưu tiên
10. `dcg.sla.policy`     – Chính sách SLA (có chatter)

### Nhóm tài chính / chi phí
11. `dcg.expense.type` – Loại chi phí
12. `dcg.cost.center`  – Cost center

### Nhóm dashboard / KPI / rule
13. `dcg.kpi.target` – Mục tiêu KPI (có chatter)
14. `dcg.alert.rule` – Quy tắc cảnh báo (có chatter)

## Phụ thuộc

- `base`, `mail`, `hr`, `resource`

## Cài đặt

1. Copy thư mục `dcg_master_data` vào `addons/` của Odoo 18.
2. Khởi động Odoo với cờ `-u dcg_master_data` hoặc cập nhật App List, tìm
   **DCG Master Data** và Install.
3. Mở menu **DCG Configuration** để quản trị master data.

## Quyền truy cập

| Group                                | Quyền                       |
|--------------------------------------|-----------------------------|
| `DCG Master Data / User`             | chỉ đọc toàn bộ master data |
| `DCG Master Data / Manager`          | tạo / sửa / xoá / lưu trữ   |

Group **Manager** mặc định được gán cho user `admin`.

## I18N

Module có sẵn bản dịch tiếng Việt tại `i18n/vi.po`. Khi cài bằng tiếng Việt
(ngôn ngữ vi_VN), giao diện sẽ hiển thị bằng tiếng Việt.

Nếu chưa load tiếng Việt:

```
Settings → Translations → Languages → Activate → Vietnamese (vi_VN)
Settings → Translations → Load a Translation → Vietnamese → with Overwrite
```

Sau đó nâng cấp module:

```
./odoo-bin -u dcg_master_data --load-language=vi_VN
```

## Dữ liệu mẫu (seed)

Module tự động seed các record sau (noupdate=1, chỉ nạp lần đầu install):

- **Ticket Severity**: Critical, High, Medium, Low
- **Ticket Priority**: P1, P2, P3, P4
- **Ticket Type**: Incident, Bug, Service Request, Change Request, Consultation, Training Support
- **Expense Type**: Taxi, Hotel, Meal, Travel, License, Subcontractor
- **Contract Type**: Implementation, Support, Maintenance
- **Acceptance Type**: Phase, UAT, Go-live

## Tích hợp với phase sau

Module này là phụ thuộc cho các module sẽ phát triển ở phase sau:

- `dcg_crm_presales` (dùng `dcg.customer.industry`, `dcg.customer.source`, `dcg.service.catalog`)
- `dcg_contract_management` (dùng `dcg.contract.type`, `dcg.contract.appendix.type`, `dcg.acceptance.type`)
- `dcg_business_trip` (dùng `dcg.expense.type`)
- `dcg_helpdesk_warranty` (dùng `dcg.ticket.*`, `dcg.sla.policy`)
- `dcg_project_finance` (dùng `dcg.cost.center`, `dcg.expense.type`, KPI/alert)

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
