# DCG Approval Matrix

Approval engine tổng quát cho mọi document nghiệp vụ DCG, trên nền **Odoo 18 Community**.
Module này phụ thuộc `dcg_master_data` (chỉ dùng chung category DCG).

## 6 model

1. `dcg.approval.matrix` – Header ma trận duyệt (theo approval_type / company / department / amount range)
2. `dcg.approval.matrix.line` – Step cấu hình trong matrix (approver: specific_user / group / employee_manager)
3. `dcg.approval.request` – Phiếu duyệt runtime, là model trung tâm chứa state, current step, action approve/reject/cancel
4. `dcg.approval.request.step` – Snapshot runtime của từng step (để audit, không phụ thuộc matrix bị sửa sau)
5. `dcg.approval.log` – Audit trail (submit / approve / reject / cancel)
6. `dcg.approval.mixin` – Abstract model để document nghiệp vụ kế thừa

Cộng 2 wizard: `dcg.approval.reject.wizard`, `dcg.approval.cancel.wizard`.

## Cách tích hợp vào module nghiệp vụ

```python
class DcgContract(models.Model):
    _name = 'dcg.contract'
    _inherit = ['dcg.approval.mixin', 'mail.thread', 'mail.activity.mixin']

    amount_total = fields.Float()
    department_id = fields.Many2one('hr.department')

    def _get_approval_type(self):
        self.ensure_one()
        return 'contract_approval'

    def _get_approval_amount(self):
        self.ensure_one()
        return self.amount_total

    def _validate_before_submit_approval(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Contract must have a customer before submitting."))

    def _approval_approved_callback(self, request):
        self.ensure_one()
        super()._approval_approved_callback(request)
        self.write({'state': 'active'})
```

Trên view document, thêm nút:

```xml
<button name="action_submit_approval" type="object" string="Submit Approval"
        invisible="approval_state == 'waiting'"/>
<button name="action_view_approval_request" type="object" string="View Approval"
        invisible="not approval_request_id"/>
```

Và để khóa field quan trọng khi đang chờ duyệt: dùng field `approval_readonly` trong `readonly="approval_readonly"`.

## Approver type (Phase 1)

| Loại                 | Cách resolve                                              |
|----------------------|------------------------------------------------------------|
| `specific_user`      | Lấy đúng `user_id` cấu hình trên step                      |
| `group`               | Bất kỳ user nội bộ active nào trong `group_id` đều được duyệt |
| `employee_manager`   | `requester_employee.parent_id.user_id` (chỉ hỗ trợ level 1) |

## Engine match matrix

Thứ tự ưu tiên khi nhiều matrix cùng `approval_type`:

1. company khớp + department khớp
2. company khớp + department rỗng
3. company rỗng + department khớp
4. company rỗng + department rỗng

Trong cùng mức, ưu tiên `sequence` nhỏ hơn. Nếu vẫn có nhiều matrix cùng mức cùng `sequence` → raise lỗi yêu cầu rà soát cấu hình (không tự chọn bừa).

## Flow runtime

```
action_submit_approval()
  -> _find_approval_matrix()
  -> _get_applicable_matrix_lines()
  -> tạo dcg.approval.request + dcg.approval.request.step (snapshot)
  -> activate step đầu (set current_approver_user_ids, tạo activity)
  -> document.approval_state = waiting

action_approve() trên request
  -> step hiện tại -> approved
  -> tìm next pending step
       còn -> activate step kế tiếp
       hết -> request.approved + callback _approval_approved_callback

action_reject(reason) trên request
  -> step hiện tại -> rejected, các step sau -> cancelled
  -> request.rejected + callback _approval_rejected_callback

action_cancel(reason) trên request
  -> mọi step pending -> cancelled
  -> request.cancelled + callback _approval_cancelled_callback
```

Sau reject, document sửa lại và **submit sẽ tạo request mới** (không tái sử dụng request cũ) — giữ audit rõ ràng.

## Phân quyền

| Group                          | Quyền                                                              |
|---------------------------------|---------------------------------------------------------------------|
| `DCG Approval / User`          | Submit document, xem request mình là requester/participant, approve nếu là current approver |
| `DCG Approval / Manager`        | Toàn quyền cấu hình matrix, xem mọi request, cancel khi cần          |

Record rule dùng field `participant_user_ids` (snapshot requester + toàn bộ approver mọi step) để user vẫn xem lại được request cũ sau khi step đã đóng.

## Menu

```
Approvals
├── Operations
│   ├── My Approvals      (state=waiting, current user là current approver)
│   ├── My Requests       (requester_id = current user)
│   ├── All Requests      (chỉ Manager)
│   └── Approval Logs     (chỉ Manager)
└── Configuration
    └── Approval Matrices (chỉ Manager)
```

## I18N

Bản dịch tiếng Việt đầy đủ tại `i18n/vi.po` — cover toàn bộ field label, selection, message lỗi
(`ValidationError`/`UserError`), action name, view string, act_window help.

Sau khi cài, để nạp:

```
Settings → Translations → Languages → Activate "Vietnamese (vi_VN)"
./odoo-bin -d <db> -u dcg_approval_matrix --load-language=vi_VN --stop-after-init
```

## Giới hạn Phase 1 (chưa làm)

- Parallel approval (nhiều người phải duyệt cùng lúc)
- Delegate approver / escalation / SLA quá hạn
- `department_manager`, `project_manager` approver type
- Auto-approve theo threshold
- Email notification (hiện chỉ dùng `mail.activity`)
- Parse `condition_json` (hiện chỉ lưu, chưa áp dụng logic)

## Cài đặt

```bash
cp -r dcg_master_data dcg_approval_matrix /path/to/odoo/addons/
./odoo-bin -d <db> -i dcg_master_data,dcg_approval_matrix --load-language=vi_VN --stop-after-init
```

## Tác giả

Công ty TNHH Đổi Mới G.R.O.U.P
