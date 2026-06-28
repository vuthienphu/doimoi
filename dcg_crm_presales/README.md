# DCG CRM Presales

Mở rộng CRM/Sales để quản lý toàn bộ giai đoạn trước hợp đồng, trên nền **Odoo 18 Community**.
Module phụ thuộc `dcg_master_data` và `dcg_approval_matrix`.

## 7 model logic (2 extend + 5 mới)

### Extend model có sẵn
1. **`res.partner`** — phân loại khách hàng B2B (`is_company_customer`, `partner_status`, `customer_rank_level`, `cooperation_status`, `debt_risk_level`, `support_level`), AM phụ trách, ngành/nguồn riêng của DCG (`dcg_industry_id`, `source_id`), smart button Opportunities/Quotations.
2. **`crm.lead`** — trung tâm điều phối presales: business discovery, estimate summary (sync từ estimate), `commercial_status` (song song với `stage_id` CRM gốc), deal approval qua `dcg.approval.mixin`.

### Model mới
3. **`dcg.crm.requirement`** — biên bản khảo sát yêu cầu (1 lead nhiều requirement, theo version).
4. **`dcg.crm.solution.scope`** — hạng mục giải pháp đề xuất (implementation/customization/integration/...).
5. **`dcg.crm.estimate`** — effort/cost/revenue/timeline theo version, có cờ `is_current_version`/`is_approved_version`.
6. **`dcg.crm.estimate.line`** — chi tiết estimate theo hạng mục, tự tổng hợp lên header.
7. **`dcg.crm.presales.cost`** — chi phí trước bán hàng (khảo sát, demo, đi lại...).

## Lưu ý quan trọng về field trùng tên với Odoo core

`res.partner` gốc của Odoo đã có field `industry_id` (Many2one tới `res.partner.industry`). Để
tránh đè field này, module đặt tên field riêng là **`dcg_industry_id`** (Many2one tới
`dcg.customer.industry`). Trên `crm.lead`, Odoo gốc không có field `industry_id` nên module
giữ nguyên tên `industry_id` nhưng label hiển thị là "DCG Industry" để tránh nhầm lẫn.

`crm.lead` gốc đã có field `source_id` (Many2one tới `utm.source` — nguồn marketing kỹ thuật).
Field riêng của DCG được đặt tên **`lead_source_id`** (Many2one tới `dcg.customer.source`) để
không xung đột.

## Approval (phase 1)

Approval bám vào `crm.lead`, không bám vào requirement/scope/cost riêng lẻ:

```python
def _get_approval_type(self):
    return 'deal_approval'

def _get_approval_amount(self):
    return self.estimated_revenue or self.expected_revenue or 0.0
```

`dcg.crm.estimate` có sẵn field `approval_required`/`approval_state`/`approval_request_id`
nhưng **không tự submit approval** — chỉ để dự phòng nếu sau này muốn chuyển sang
approval-theo-từng-estimate mà không phải đổi schema.

## Logic estimate version (quan trọng)

- `action_set_current_version()`: clear cờ `is_current_version` ở các estimate khác cùng lead,
  set cờ ở bản ghi này, đồng bộ summary lên lead.
- `action_mark_approved_version()`: tương tự với `is_approved_version`, đồng thời set
  `lead.approved_estimate_id` và chuyển `state = approved`.
- Lead luôn ưu tiên hiển thị theo: **approved estimate → current estimate → latest estimate**
  (logic nằm trong `_sync_to_lead()`, gọi mỗi khi set current/approved).

## Tạo quotation (Cách 1.5 theo spec)

`action_create_quotation()` trên lead tạo `sale.order` header (partner, currency, note từ
scope summary) — **không tự sinh line** từ estimate/scope để tránh CPQ phức tạp sớm; line do
user bổ sung tay sau khi mở quotation.

## View — các điểm kỹ thuật đã verify trực tiếp với Odoo 18 source

Vì `crm.lead`/`res.partner` là model lõi rất phức tạp, các view extension trong module này được
viết dựa trên **source code thật của Odoo 18** (không suy đoán):

- `res.partner`: xpath neo vào `div[@name='button_box']` (self-closing trong base view, vẫn
  nhận `position="inside"`), `field[@name='category_id']`, `page[@name='sales_purchases']`.
- `crm.lead` form: neo vào `field[@name='stage_id']` (duy nhất, trong `<header>`),
  `div[hasclass('o_lead_opportunity_form_inline_fields')]` (duy nhất), `page[@name='internal_notes']`.
- `crm.lead` list: kế thừa `crm.crm_case_tree_view_oppor`, neo vào `field[@name='stage_id']`.
- `crm.lead` search: kế thừa `crm.view_crm_case_opportunities_filter`, neo vào
  `filter[@name='assigned_to_me']` và `filter[@name='salesperson']`.

Nếu nâng cấp lên Odoo version khác, các anchor field/page trên cần verify lại vì core view có
thể thay đổi cấu trúc.

## Security

| Group | Quyền |
|---|---|
| `DCG Presales / User` | CRUD requirement/scope/estimate/cost cho lead mình phụ trách (salesperson, presales owner, hoặc team member) |
| `DCG Presales / Manager` | Toàn quyền, xem tất cả |

`crm.lead` không tạo access mới (dùng access gốc của module `crm`), chỉ extend field/view/logic.

## I18N

`i18n/vi.po` — 245 entry, 100% dịch. Cover field label, help text, selection, view string,
button, search filter, message lỗi Python, và `ir.actions.act_window` help text.

```
Settings → Translations → Languages → Activate "Vietnamese (vi_VN)"
./odoo-bin -d <db> -u dcg_crm_presales --load-language=vi_VN --stop-after-init
```

## Cài đặt

```bash
cp -r dcg_master_data dcg_approval_matrix dcg_crm_presales /path/to/odoo/addons/
./odoo-bin -d <db> -i dcg_master_data,dcg_approval_matrix,dcg_crm_presales \
    --load-language=vi_VN --stop-after-init
```

## Giới hạn Phase 1 (chưa làm)

- CPQ / pricing engine phức tạp
- Presales task management kiểu mini-project
- Resource booking cho presales
- Document/proposal generation hoàn chỉnh
- Win/loss analytics sâu
- Multi-version scope diff nâng cao
- Portal khách hàng
- Approval theo từng estimate (hiện chỉ approval theo lead)

## Module tiếp theo

`dcg_contract_management` — nhận trực tiếp từ `crm.lead`/`dcg.crm.estimate`/`sale.order` để
tạo hợp đồng, theo flow: **Lead → Requirement → Scope → Estimate → Approval → Quotation → Contract**.

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
