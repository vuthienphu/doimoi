# DCG Project Finance

Lớp tài chính dự án — P&L, budget vs actual, cost/revenue tracking, finance health, trên nền **Odoo 18 Community**.

## Vị trí trong chuỗi module DCG

```
dcg_master_data → dcg_approval_matrix → dcg_crm_presales → dcg_contract_management
  → dcg_project_delivery → dcg_timesheet_control → dcg_project_finance
```

## 3 model mới + 2 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.project.finance` | Header P&L: planned/actual revenue-cost-margin, collection, effort, variance, health |
| 2 | `dcg.project.finance.cost.line` | Chi phí chi tiết: labor (từ timesheet), travel, subcontract, manual |
| 3 | `dcg.project.finance.revenue.line` | Doanh thu/collection: từ payment schedule, appendix, manual |
| 4 | `dcg.project.delivery` (extend) | `finance_id`, `action_create_finance()` auto-snapshot |
| 5 | `dcg.contract` (extend) | `finance_record_id` compute link |

## Flow chính

```
Contract/Estimate → Project Finance (auto snapshot planned)
  → Sync Revenue from contract payments
  → Timesheet approved → Refresh Costs → labor cost lines
  → Manual cost (travel/subcontract/expense)
  → P&L: planned vs actual margin
  → Finance health: green/yellow/red
  → Collection tracking: invoiced → collected → outstanding
```

## Finance Health auto-compute (spec mục 67-68)

```python
# Red: actual_margin < 0 HOẶC actual_cost > planned_cost × 1.15
# Yellow: actual_cost > planned_cost HOẶC collection chậm so với progress
# Green: còn lại
```

## 2 sync action chính

**Sync Revenue** (`action_sync_revenue_from_contract`): tạo/update revenue line cho mỗi `dcg.contract.payment`, map planned_amount, invoiced/collected status.

**Refresh Costs** (`action_refresh_actual_cost`): tạo/update cost line loại `labor` cho mỗi approved timesheet line, idempotent theo `timesheet_line_id`.

## Actual revenue = invoiced_amount (spec mục 66/90)

Phase 1 dùng `actual_revenue = sum(revenue_line.invoiced_amount)` — rõ ràng, dễ kiểm soát. Nếu sau cần revenue recognition phức tạp hơn thì thêm field `recognized_revenue` riêng.

## I18N

`i18n/vi.po` — 129 entry, 100% dịch, **đúng format Odoo 18** với `#:` reference path:
- `model:ir.model.fields,field_description:module.field_model__field`
- `model:ir.model.fields.selection,name:module.selection__model__field__value`
- `model_terms:ir.ui.view,arch_db:module.view_id`
- `code:addons/module/models/file.py:0`

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
