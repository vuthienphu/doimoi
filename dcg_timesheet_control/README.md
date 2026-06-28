# DCG Timesheet Control

Quản lý chấm công, kiểm soát effort, billable/OT, approval theo kỳ, trên nền **Odoo 18 Community**.

## Vị trí trong chuỗi module DCG

```
dcg_master_data → dcg_approval_matrix → dcg_crm_presales → dcg_contract_management
  → dcg_project_delivery → dcg_timesheet_control
```

## Kiến trúc: extend Odoo timesheet, không tạo line model riêng

Module **extend `account.analytic.line`** (timesheet line lõi của Odoo) thay vì tạo model riêng,
để tận dụng nền hr_timesheet/analytic sẵn có. Lớp quản trị bổ sung qua `dcg.timesheet.sheet`.

## 2 model mới + 3 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.timesheet.sheet` | Phiếu chấm công theo kỳ (tuần/tháng), submit/approve |
| 2 | `dcg.timesheet.ot.request` | Yêu cầu tăng ca với approval riêng |
| 3 | `account.analytic.line` (extend) | +18 field: delivery project, scope, charge_type, OT, costing |
| 4 | `dcg.project.delivery` (extend) | actual hours tổng hợp từ approved lines |
| 5 | `dcg.project.scope` (extend) | actual hours tổng hợp từ approved lines |

## Flow chính

```
User ghi line hằng ngày (project/scope/giờ/billable)
  → Cuối kỳ: Generate Sheet (wizard) hoặc tạo tay
    → action_load_lines() nạp line draft vào sheet
      → Submit → Approver duyệt
        → line_state sync 'approved'
          → project/scope actual_hours recompute
```

## Sheet = đơn vị approval (spec mục 50)

- 1 employee + 1 kỳ = 1 sheet (SQL constraint unique)
- Line state đồng bộ theo sheet: draft/submitted/approved/rejected
- Line trong approved sheet readonly (spec mục 34)
- Manager có thể reset approved sheet (spec mục 84)

## Classification giờ công (spec mục 29)

- `work_type`: project_delivery, support, internal, presales, training, leave_related, other
- `charge_type`: billable, non_billable, investment
- `is_billable` auto-compute từ charge_type
- `is_overtime` + `overtime_hours` cho OT tracking

## Costing fields (spec mục 31)

Sẵn sàng cho `dcg_project_finance`:
- `cost_rate`, `billing_rate` (đơn giá)
- `line_cost_amount = unit_amount × cost_rate` (compute)
- `line_billing_amount = unit_amount × billing_rate` (compute)

## Project actual sync (spec mục 45)

Chỉ tính **approved lines**:
- `dcg.project.scope.ts_actual_hours` = sum approved lines by scope
- `dcg.project.delivery.total_actual_hours` = sum approved lines by project
- Breakdown: billable, non-billable, OT riêng

## OT Request (spec mục 36-41)

- Approval riêng (approver = employee's manager)
- `ot_request_id` trên timesheet line để link
- Compute `total_hours` từ `date_from/date_to`
- Phase 1: không block cứng nếu line OT không có request

## Security — 3 cấp

| Group | Quyền |
|---|---|
| `DCG Timesheet / User` | CRUD sheet/line/OT của mình |
| `DCG Timesheet / Approver` | + approve sheet/OT cấp dưới |
| `DCG Timesheet / Manager` | Toàn quyền, reset approved sheet |

## Menu

```
Timesheets (app root)
├── My Timesheet Sheets (default: my filter)
├── Sheets to Approve (approver+)
├── Timesheet Lines
├── OT Requests
└── Generate Sheet (wizard)
```

## I18N

`i18n/vi.po` — 122 entry, 100% dịch.

## Cài đặt

```bash
./odoo-bin -d <db> \
    -i dcg_master_data,dcg_approval_matrix,dcg_crm_presales,dcg_contract_management,dcg_project_delivery,dcg_timesheet_control \
    --load-language=vi_VN --stop-after-init
```

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
