# DCG Project Delivery

Quản lý triển khai dự án sau khi có hợp đồng, trên nền **Odoo 18 Community**.

## Vị trí trong chuỗi module DCG

```
dcg_master_data → dcg_approval_matrix → dcg_crm_presales → dcg_contract_management → dcg_project_delivery
```

## 6 model mới + 1 extend

| # | Model | Vai trò |
|---|---|---|
| 1 | `dcg.project.delivery` | Header dự án, 8 trạng thái, health status auto-compute |
| 2 | `dcg.project.scope` | Work package với effort snapshot + progress tracking |
| 3 | `dcg.project.milestone` | Mốc triển khai, gắn payment + acceptance |
| 4 | `dcg.project.member` | Thành viên với role/allocation/billable |
| 5 | `dcg.project.issue` | Issue/risk/blocker, drive project health_status |
| 6 | `dcg.project.change.request` | CR với impact analysis, button tạo contract appendix |
| 7 | `dcg.contract` (extend) | `action_create_project()`, map contract lines → project scope |

## Luồng state project (8 trạng thái)

```
draft → ready → in_progress → on_hold (tạm dừng, có thể quay lại in_progress)
                             → uat → done → closed
                                           ↘ cancelled (bất kỳ lúc nào trước closed)
```

## Tạo project từ contract

`dcg.contract.action_create_project()`:

1. Map header: partner, currency, PM, delivery owner, presales owner, timeline, finance snapshot
2. Map scope/handover note từ contract
3. **Map contract lines → project scope** (1:1), kèm effort snapshot (ba/dev/test/pm/support hours)
4. Set `contract.project_created = True`, `contract.primary_project_id`

## Health status auto-compute (spec mục 44)

```python
# Có issue critical đang open → red
# Có issue high đang open → yellow  
# Không có issue nghiêm trọng → green
```

Compute trigger: `issue_ids.priority` + `issue_ids.state`. Stored field, tự cập nhật khi issue thay đổi.

## Progress compute (spec mục 53)

```python
progress_percent = average(scope.progress_percent)  # chỉ scope chưa cancelled
```

PM nhập `progress_percent` trên từng scope, project tự tổng hợp.

## Change Request → Contract Appendix (spec mục 49)

Khi CR được approved, user bấm **"Create Appendix"**:
- Tự sinh `dcg.contract.appendix` với `appendix_type = 'scope_change'`
- Map `value_delta`, `old_amount_total`, `old_end_date`, `new_end_date`, `reason`
- Link `cr.appendix_id` để trace ngược
- **Không tự động** — user chủ động bấm, vì không phải CR nào cũng cần appendix

## Milestone ↔ Payment ↔ Acceptance

Milestone có thể link:
- `contract_payment_id` → mốc nào unlock thanh toán nào
- `acceptance_id` → mốc nào gắn biên bản nghiệm thu nào

Giúp PM + finance nhìn được: milestone done → payment waiting → acceptance confirmed → payment paid.

## Menu

```
Delivery (app root)
├── Projects
├── Milestones
├── Issues / Risks
└── Change Requests
```

## Security

| Group | Quyền |
|---|---|
| `DCG Delivery / User` | CRUD project/scope/milestone/member/issue/CR (không xoá project/issue/CR) |
| `DCG Delivery / Manager` | Toàn quyền, close project, override state |

## I18N

`i18n/vi.po` — 205 entry, 100% dịch.

## Cài đặt

```bash
cp -r dcg_master_data dcg_approval_matrix dcg_crm_presales \
      dcg_contract_management dcg_project_delivery \
      /path/to/odoo/addons/

./odoo-bin -d <db> \
    -i dcg_master_data,dcg_approval_matrix,dcg_crm_presales,dcg_contract_management,dcg_project_delivery \
    --load-language=vi_VN --stop-after-init
```

## Giới hạn Phase 1

- Chưa Gantt/kanban task engine
- Chưa budget actual finance chi tiết
- Chưa resource allocation tối ưu
- Chưa subcontractor delivery
- Chưa auto sync timesheet (chuẩn bị data cho `dcg_timesheet_control`)
- Appendix `update`/`remove` từ CR chỉ ghi nhận — chưa auto sửa scope

## Module tiếp theo

`dcg_timesheet_control` — lúc đó đã có đầy đủ project, scope, member, planned effort
để build timesheet + actual effort + cost tracking.

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
