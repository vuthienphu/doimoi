# DCG Contract Management

Quản lý toàn bộ vòng đời hợp đồng dịch vụ/dự án, trên nền **Odoo 18 Community**.

## Vị trí trong chuỗi module DCG

```
dcg_master_data → dcg_approval_matrix → dcg_crm_presales → dcg_contract_management
```

## 6 model mới + 2 extend

### Model mới
| # | Model | Vai trò | Approval |
|---|---|---|---|
| 1 | `dcg.contract` | Header hợp đồng, 8 trạng thái business | `contract_approval` |
| 2 | `dcg.contract.line` | Hạng mục / scope với effort snapshot | — |
| 3 | `dcg.contract.payment` | Lịch thanh toán (%, cố định), 5 trạng thái | — |
| 4 | `dcg.contract.appendix` | Phụ lục hợp đồng, áp dụng thay đổi lên contract | `appendix_approval` |
| 5 | `dcg.contract.appendix.line` | Chi tiết thay đổi (add/update/remove scope) | — |
| 6 | `dcg.contract.acceptance` | Biên bản nghiệm thu (phase/milestone/final/warranty) | — |

### Extend model có sẵn
7. **`sale.order`** — `action_create_contract()` tạo contract từ quotation, map estimate lines → contract lines
8. **`crm.lead`** — `contract_count`, `primary_contract_id`, smart button xem contracts

## Luồng state contract (8 trạng thái)

```
draft → waiting_approval → approved → active → in_progress → done → closed
                                                                  ↘ cancelled (bất kỳ lúc nào trước closed)
```

- **draft → waiting_approval**: user bấm "Submit Approval", engine `dcg_approval_matrix` sinh request
- **waiting_approval → approved**: tất cả step trong matrix approved, callback chuyển state
- **approved → active**: user bấm "Activate Contract" (xác nhận đã ký / hiệu lực)
- **active → in_progress**: bắt đầu triển khai
- **in_progress → done**: hoàn thành nghĩa vụ chính / nghiệm thu final
- **done → closed**: đóng hợp đồng (qua wizard Close Contract)

## Approval tích hợp

2 loại approval type riêng:

| Document | approval_type | _get_approval_amount() |
|---|---|---|
| `dcg.contract` | `contract_approval` | `amount_total` |
| `dcg.contract.appendix` | `appendix_approval` | `abs(value_delta)` |

Cả hai đều inherit `dcg.approval.mixin`, override `_validate_before_submit_approval()` và
callback `_approval_approved_callback()` / `_approval_rejected_callback()`.

## Tạo contract từ quotation

`sale.order.action_create_contract()` thực hiện:
1. Map header: partner, currency, amount, lead, estimate, AM/presales owner
2. Map `scope_summary`, `handover_note`, `expected_cost` từ lead/estimate
3. **Map estimate lines → contract lines** (nếu lead có `approved_estimate_id` hoặc `latest_estimate_id`):
   mỗi `dcg.crm.estimate.line` sinh 1 `dcg.contract.line` với effort snapshot (ba/dev/test/pm/support hours)
4. Set `quotation.contract_created = True`

## Phụ lục — `_apply_appendix_to_contract()`

Khi appendix được đánh dấu "Effective" (sau khi approved):
1. `contract.amount_total += value_delta`
2. `contract.end_date = new_end_date` (nếu gia hạn)
3. Appendix line có `change_type = 'add'` → sinh `dcg.contract.line` mới trên contract

Appendix draft/waiting **không** tác động contract — chỉ khi effective.

## Payment schedule

- `payment_type = 'percent'`: auto compute `amount = contract.amount_total * percent / 100`
- `payment_type = 'fixed'`: `amount` nhập tay
- `balance_amount = amount - amount_received` (compute)
- State: `draft → waiting → partial → paid` (hoặc cancelled)

## Nghiệm thu

- 4 loại: Phase, Milestone, Final, Warranty/Handover
- Liên kết với `payment_id` và `appendix_id` để theo dõi
- State: `draft → confirmed → cancelled`

## Menu

```
Contracts (app root)
├── Contracts
├── Payment Schedules
├── Appendices
└── Acceptances
```

## Security

| Group | Quyền |
|---|---|
| `DCG Contract / User` | CRUD (không xoá contract/payment/appendix/acceptance) |
| `DCG Contract / Manager` | Toàn quyền kể cả xoá, close contract, mark appendix effective |

User không có quyền `unlink` trên contract/payment/appendix/acceptance (chỉ Manager). Tất cả
user đều có quyền `unlink` trên contract line và appendix line (inline editing).

## I18N

`i18n/vi.po` — 213 entry, 100% dịch. Cover tất cả field, selection (8 contract state, 6 contract
type, 5 payment state, 4 appendix type, 4 acceptance type, 3 change type...), button, view tab,
group title, error message Python.

## Cài đặt

```bash
cp -r dcg_master_data dcg_approval_matrix dcg_crm_presales dcg_contract_management \
    /path/to/odoo/addons/
./odoo-bin -d <db> \
    -i dcg_master_data,dcg_approval_matrix,dcg_crm_presales,dcg_contract_management \
    --load-language=vi_VN --stop-after-init
```

## Lưu ý khi test

1. **Trước khi test approval**: phải cấu hình matrix với `approval_type = 'contract_approval'`
   và `'appendix_approval'` trong menu Approvals → Configuration → Approval Matrices.
2. **Tạo contract từ quotation**: cần lead có estimate (approved/current) để map lines tự động.
   Nếu không có estimate, contract header vẫn tạo được nhưng lines trống.
3. **View sale.order**: xpath `//div[@name='button_box']` và `sale.view_order_form` /
   `sale.view_order_tree` — nếu module sale bị custom nặng bởi module khác, cần verify
   không xung đột.

## Giới hạn Phase 1

- Chưa sync invoice/accounting
- Chưa retention/guarantee phức tạp
- Chưa auto revenue recognition
- Chưa vendor/subcontract contract
- Chưa e-signature
- Chưa contract document generation
- Appendix `update`/`remove` chỉ ghi nhận — chưa auto sửa/xoá contract line tương ứng
  (phase 1 chỉ xử lý `add`)

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
