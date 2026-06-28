# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


APPROVAL_STATE_SELECTION = [
    ('not_required', 'Not Required'),
    ('draft', 'Draft'),
    ('waiting', 'Waiting Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class DcgApprovalMixin(models.AbstractModel):
    """Mixin chuẩn để document nghiệp vụ tích hợp với approval engine.

    Cách dùng tối thiểu trong document nghiệp vụ::

        class DcgContract(models.Model):
            _name = 'dcg.contract'
            _inherit = ['dcg.approval.mixin', 'mail.thread', 'mail.activity.mixin']

            def _get_approval_type(self):
                self.ensure_one()
                return 'contract_approval'

            def _get_approval_amount(self):
                self.ensure_one()
                return self.amount_total

            def _approval_approved_callback(self, request):
                self.ensure_one()
                self.write({'state': 'active'})
    """
    _name = 'dcg.approval.mixin'
    _description = 'DCG Approval Mixin'

    # ============================================================
    # Fields
    # ============================================================
    approval_request_id = fields.Many2one(
        'dcg.approval.request',
        string='Approval Request',
        copy=False,
        readonly=True,
        tracking=True,
    )
    approval_state = fields.Selection(
        selection=APPROVAL_STATE_SELECTION,
        string='Approval Status',
        default='draft',
        copy=False,
        readonly=True,
        tracking=True,
        index=True,
    )
    approval_submitted_by = fields.Many2one(
        'res.users',
        string='Submitted By',
        copy=False,
        readonly=True,
    )
    approval_submitted_date = fields.Datetime(
        string='Submitted On',
        copy=False,
        readonly=True,
    )
    approval_last_action_by = fields.Many2one(
        'res.users',
        string='Approval Last Action By',
        copy=False,
        readonly=True,
    )
    approval_last_action_date = fields.Datetime(
        string='Approval Last Action On',
        copy=False,
        readonly=True,
    )
    approval_reject_reason = fields.Text(
        string='Approval Reject Reason',
        copy=False,
        readonly=True,
    )
    approval_readonly = fields.Boolean(
        string='Locked by Approval',
        compute='_compute_approval_readonly',
    )

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('approval_state')
    def _compute_approval_readonly(self):
        for rec in self:
            rec.approval_readonly = rec._is_approval_locked()

    # ============================================================
    # Hooks – override in concrete document models
    # ============================================================
    def _get_approval_type(self):
        """Bắt buộc override. Trả về một mã trong APPROVAL_TYPE_SELECTION."""
        self.ensure_one()
        raise NotImplementedError(_(
            "Model '%s' must implement _get_approval_type()."
        ) % self._name)

    def _get_approval_amount(self):
        """Trả về amount để engine lọc step. Mặc định 0.0."""
        self.ensure_one()
        return 0.0

    def _get_approval_currency(self):
        self.ensure_one()
        if 'currency_id' in self._fields and self.currency_id:
            return self.currency_id
        return self.env.company.currency_id

    def _get_approval_requester(self):
        self.ensure_one()
        return self.env.user

    def _get_approval_requester_employee(self):
        self.ensure_one()
        user = self._get_approval_requester()
        return self.env['hr.employee'].search(
            [('user_id', '=', user.id)], limit=1
        )

    def _get_approval_department(self):
        """Mặc định lấy department từ requester employee, nếu không có thì False."""
        self.ensure_one()
        employee = self._get_approval_requester_employee()
        if employee and employee.department_id:
            return employee.department_id
        if 'department_id' in self._fields and self.department_id:
            return self.department_id
        return self.env['hr.department'].browse()

    def _get_approval_company(self):
        self.ensure_one()
        if 'company_id' in self._fields and self.company_id:
            return self.company_id
        return self.env.company

    def _get_approval_res_name(self):
        self.ensure_one()
        return self.display_name

    def _validate_before_submit_approval(self):
        """Override để validate trước khi cho submit. Raise UserError nếu fail."""
        self.ensure_one()
        return True

    def _is_approval_locked(self):
        """Document có bị khóa do approval không? Mặc định: True khi đang waiting."""
        self.ensure_one()
        return self.approval_state == 'waiting'

    # ---- Callbacks: override theo nghiệp vụ ----
    def _approval_approved_callback(self, request):
        self.ensure_one()
        self.write({
            'approval_state': 'approved',
            'approval_last_action_by': self.env.uid,
            'approval_last_action_date': fields.Datetime.now(),
        })

    def _approval_rejected_callback(self, request):
        self.ensure_one()
        self.write({
            'approval_state': 'rejected',
            'approval_reject_reason': request.reject_reason or '',
            'approval_last_action_by': self.env.uid,
            'approval_last_action_date': fields.Datetime.now(),
        })

    def _approval_cancelled_callback(self, request):
        self.ensure_one()
        self.write({
            'approval_state': 'cancelled',
            'approval_last_action_by': self.env.uid,
            'approval_last_action_date': fields.Datetime.now(),
        })

    # ============================================================
    # Engine entry points
    # ============================================================
    def _find_approval_matrix(self):
        self.ensure_one()
        approval_type = self._get_approval_type()
        company = self._get_approval_company()
        department = self._get_approval_department()
        amount = self._get_approval_amount() or 0.0
        Matrix = self.env['dcg.approval.matrix'].sudo()
        matrix = Matrix._find_best_matrix(
            approval_type=approval_type,
            company=company,
            department=department,
            amount=amount,
        )
        if not matrix:
            raise UserError(_(
                "No approval matrix found for type '%(t)s' (company=%(c)s, department=%(d)s, amount=%(a)s)."
            ) % {
                't': approval_type,
                'c': company.display_name if company else '-',
                'd': department.display_name if department else '-',
                'a': amount,
            })
        return matrix

    def _get_applicable_matrix_lines(self, matrix):
        """Lọc line áp dụng theo amount, sắp xếp theo sequence."""
        self.ensure_one()
        amount = self._get_approval_amount() or 0.0
        lines = matrix.line_ids.filtered(
            lambda l: l.active and l.is_applicable_for_amount(amount)
        ).sorted(key=lambda l: (l.sequence, l.id))
        if not lines:
            raise UserError(_(
                "Matrix '%(m)s' has no applicable approval step for amount %(a)s."
            ) % {'m': matrix.display_name, 'a': amount})
        return lines

    def _build_step_vals(self, line, requester_employee):
        self.ensure_one()
        approvers = line.resolve_approver_users(requester_employee=requester_employee)
        return {
            'sequence': line.sequence,
            'matrix_line_id': line.id,
            'name': line.name or _('Step %s') % line.sequence,
            'approver_type': line.approver_type,
            'approver_user_ids': [(6, 0, approvers.ids)],
            'min_amount': line.min_amount,
            'max_amount': line.max_amount,
            'state': 'pending',
        }

    def _build_request_vals(self, matrix, requester, requester_employee, department):
        self.ensure_one()
        return {
            'approval_type': self._get_approval_type(),
            'matrix_id': matrix.id,
            'request_date': fields.Datetime.now(),
            'amount_total': self._get_approval_amount() or 0.0,
            'currency_id': self._get_approval_currency().id,
            'requester_id': requester.id,
            'requester_employee_id': requester_employee.id if requester_employee else False,
            'requester_department_id': department.id if department else False,
            'res_model': self._name,
            'res_id': self.id,
            'res_name': self._get_approval_res_name(),
            'company_id': self._get_approval_company().id,
            'state': 'waiting',
        }

    # ============================================================
    # User actions
    # ============================================================
    def action_submit_approval(self):
        for rec in self:
            # 1. validate
            if rec.approval_state == 'waiting':
                raise UserError(_(
                    "Document '%s' is already waiting for approval."
                ) % rec.display_name)
            rec._validate_before_submit_approval()

            # 2. find matrix and applicable lines
            matrix = rec._find_approval_matrix()
            lines = rec._get_applicable_matrix_lines(matrix)

            # 3. resolve requester
            requester = rec._get_approval_requester()
            requester_employee = rec._get_approval_requester_employee()
            department = rec._get_approval_department()

            # 4. precompute step vals so we can detect resolve errors before any write
            step_vals_list = [
                rec._build_step_vals(line, requester_employee) for line in lines
            ]

            # 5. create request
            request_vals = rec._build_request_vals(
                matrix=matrix,
                requester=requester,
                requester_employee=requester_employee,
                department=department,
            )
            request = self.env['dcg.approval.request'].create(request_vals)

            # 6. create steps
            for sv in step_vals_list:
                sv['request_id'] = request.id
            steps = self.env['dcg.approval.request.step'].create(step_vals_list)

            # 7. participant snapshot
            participant_ids = set([requester.id])
            for s in steps:
                participant_ids.update(s.approver_user_ids.ids)
            request.write({'participant_user_ids': [(6, 0, list(participant_ids))]})

            # 8. submit log + activate first step
            request._add_log(
                action='submit',
                from_state='draft',
                to_state='waiting',
                note=None,
            )
            request._activate_step(steps[0])

            # 9. update document
            rec.write({
                'approval_request_id': request.id,
                'approval_state': 'waiting',
                'approval_submitted_by': requester.id,
                'approval_submitted_date': fields.Datetime.now(),
                'approval_last_action_by': requester.id,
                'approval_last_action_date': fields.Datetime.now(),
                'approval_reject_reason': False,
            })
        return True

    def action_view_approval_request(self):
        self.ensure_one()
        if not self.approval_request_id:
            raise UserError(_("This document has no approval request yet."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Request'),
            'res_model': 'dcg.approval.request',
            'res_id': self.approval_request_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
