# DCG Helpdesk Warranty

Hệ thống quản lý bảo hành & hỗ trợ sau triển khai — module cuối cùng trong lifecycle dự án DCG, trên nền **Odoo 18 Community**.

## Vị trí trong chuỗi 9 module DCG

```
dcg_master_data → dcg_approval_matrix → dcg_crm_presales → dcg_contract_management
  → dcg_project_delivery → dcg_timesheet_control → dcg_project_finance
    → dcg_business_trip → dcg_helpdesk_warranty
```

## 7 model mới + 2 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.warranty.ticket.stage` | Workflow động (kanban drag & drop), SLA control per stage |
| 2 | `dcg.warranty.ticket.tag` | Tag đa chiều (module/technology/business) |
| 3 | `dcg.warranty.team` | Nhóm support (leader + members) |
| 4 | `dcg.warranty.sla` | Chính sách SLA theo severity × priority |
| 5 | `dcg.warranty.ticket` | Ticket chính — stage_id, SLA, warranty auto-compute |
| 6 | `dcg.warranty.activity` | Timeline xử lý ticket |
| 7 | `dcg.warranty.solution` | Knowledge base / giải pháp tái sử dụng |
| 8 | `dcg.contract` (extend) | `ticket_count`, smart button |
| 9 | `dcg.project.delivery` (extend) | `ticket_count`, smart button |

## Dynamic stage (không hardcode selection)

Ticket dùng `stage_id` (Many2one → `dcg.warranty.ticket.stage`) thay vì `state` Selection cố định.
Stage có flag workflow (`is_start`, `is_done`, `is_cancel`) và SLA control (`sla_running`, `pause_sla`, `stop_sla`).

9 stage mặc định: New → Assigned → Investigating → Waiting Customer → Development → Testing → Resolved → Closed / Cancelled.

Hỗ trợ **Kanban drag & drop** qua `group_expand='_read_group_stage_ids'`.

## Warranty auto-compute

```python
is_in_warranty = warranty_start_date <= today <= warranty_end_date
```

Lấy từ `contract.end_date` / `contract.warranty_end_date`.

## SLA tracking

- `sla_id` auto-lookup theo severity + priority
- `response_deadline`, `resolve_deadline` từ SLA policy
- `sla_breached` compute: `resolve_date > resolve_deadline`
- Stage `Waiting Customer` pause SLA, `Resolved` stop SLA

## Menu

```
Warranty (app root)
├── All Tickets (kanban default)
├── My Tickets
├── Solutions / KB
└── Configuration
    ├── Teams
    ├── SLA Policies
    ├── Stages
    └── Tags
```

## Security — 3 cấp

| Group | Quyền |
|---|---|
| `DCG Warranty / User` | CRUD ticket/activity, read config |
| `DCG Warranty / Leader` | + approve/review |
| `DCG Warranty / Manager` | Toàn quyền, cấu hình stage/SLA/team/tag |

## I18N

`i18n/vi.po` — 141 entry, 100%, đúng format Odoo 18 với `#:` reference path.

## Lifecycle hoàn chỉnh 9 module

```
Lead → Requirement → Estimate → Quotation
  → Contract → Approval → Project (auto scope)
    → Team → Milestones → Issues → Change Requests
      → Timesheet → Finance (P&L, variance, health)
        → Business Trip → Finance cost sync
          → Warranty Ticket → SLA → Engineer → Resolve → Close
```

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
