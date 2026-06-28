# DCG Business Trip

Quản lý công tác / onsite triển khai, nguồn chi phí travel cho project finance, trên nền **Odoo 18 Community**.

## Vị trí trong chuỗi 8 module DCG

```
dcg_master_data → dcg_approval_matrix → dcg_crm_presales → dcg_contract_management
  → dcg_project_delivery → dcg_timesheet_control → dcg_project_finance → dcg_business_trip
```

## 3 model mới + 1 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.business.trip` | Header công tác, inherit `dcg.approval.mixin` |
| 2 | `dcg.business.trip.member` | Thành viên chuyến đi (role, team lead) |
| 3 | `dcg.business.trip.expense` | Chi phí estimated/actual, trace finance sync |
| 4 | `dcg.project.delivery` (extend) | `trip_count`, `total_trip_cost`, smart button |

## Flow

```
Tạo Trip → Members + Estimated Expense → Submit Approval (dcg.approval.mixin)
  → Approved → Start Trip → Actual Expense → Mark Done
    → Sync to Finance → cost lines (travel) trong project finance
```

## Approval tích hợp

- `_get_approval_type() → 'business_trip_approval'`
- `_get_approval_amount() → estimated_cost`
- Validate: phải có member + ngày đi/về trước khi submit

## Finance sync idempotent (spec mục 48-51, 81-82)

Khi trip done, bấm **Sync to Finance**:
- Mỗi expense line `source_type = 'actual'` → tạo/update 1 `dcg.project.finance.cost.line`
- `cost_type = 'travel'`, `source_type = 'trip'`
- Trace qua `expense.finance_cost_line_id` — sync lại không tạo trùng
- Trip không gắn project → không sync

## Chi phí estimated vs actual

Cùng 1 model `dcg.business.trip.expense`, phân biệt bằng `source_type`:
- `estimated`: căn cứ approval + budget
- `actual`: chi phí thực tế sau chuyến đi
- `adjustment`: điều chỉnh

Header compute: `estimated_cost`, `actual_cost`, `cost_variance` tự tổng hợp từ lines.

## I18N

`i18n/vi.po` — 118 entry, 100%, đúng format Odoo 18.

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
