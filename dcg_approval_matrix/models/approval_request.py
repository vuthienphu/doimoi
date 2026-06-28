# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .approval_matrix import APPROVAL_TYPE_SELECTION

_logger = logging.getLogger(__name__)


REQUEST_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('waiting', 'Waiting Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class DcgApprovalRequest(models.Model):
    """Phiếu duyệt runtime — sinh khi một document submit duyệt."""
    _name = 'dcg.approval.request'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        tracking=True,
    )

    # ============================================================
    # Request context
    # ============================================================
    approval_type = fields.Selection(
        selection=APPROVAL_TYPE_SELECTION,
        string='Approval Type',
        required=True,
        tracking=True,
        index=True,
    )
    matrix_id = fields.Many2one(
        'dcg.approval.matrix',
        string='Matrix',
        ondelete='restrict',
        tracking=True,
    )
    request_date = fields.Datetime(
        string='Submitted On',
        default=fields.Datetime.now,
        tracking=True,
    )
    approved_date = fields.Datetime(string='Approved On', tracking=True)
    rejected_date = fields.Datetime(string='Rejected On', tracking=True)
    cancelled_date = fields.Datetime(string='Cancelled On', tracking=True)
    amount_total = fields.Float(string='Amount', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    note = fields.Text(string='Submission Note')

    # ============================================================
    # Requester
    # ============================================================
    requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )
    requester_employee_id = fields.Many2one('hr.employee', string='Requester Employee')
    requester_department_id = fields.Many2one('hr.department', string='Requester Department')

    # ============================================================
    # Source document
    # ============================================================
    res_model = fields.Char(string='Source Model', required=True, index=True)
    res_id = fields.Integer(string='Source ID', required=True, index=True)
    res_name = fields.Char(string='Source Name')
    source_ref = fields.Char(
        string='Source',
        compute='_compute_source_ref',
    )

    # ============================================================
    # State / Current step
    # ============================================================
    state = fields.Selection(
        selection=REQUEST_STATE_SELECTION,
        string='Status',
        required=True,
        default='draft',
        tracking=True,
        index=True,
    )
    current_step = fields.Integer(string='Current Step', tracking=True)
    current_step_id = fields.Many2one(
        'dcg.approval.request.step',
        string='Current Step Record',
        tracking=True,
    )
    current_line_id = fields.Many2one(
        'dcg.approval.matrix.line',
        string='Current Matrix Line',
        tracking=True,
    )
    current_approver_user_ids = fields.Many2many(
        'res.users',
        'dcg_approval_request_current_approver_rel',
        'request_id',
        'user_id',
        string='Current Approvers',
    )
    participant_user_ids = fields.Many2many(
        'res.users',
        'dcg_approval_request_participant_rel',
        'request_id',
        'user_id',
        string='Participants',
        help='Snapshot of requester + all candidate approvers across every step.'
             ' Used by record rules so participants keep access after the step is closed.',
    )
    last_action_by = fields.Many2one('res.users', string='Last Action By', tracking=True)
    last_action_date = fields.Datetime(string='Last Action On', tracking=True)

    # ============================================================
    # Result
    # ============================================================
    reject_reason = fields.Text(string='Reject Reason')
    cancel_reason = fields.Text(string='Cancel Reason')
    result_note = fields.Text(string='Result Note')
    final_approver_id = fields.Many2one('res.users', string='Final Approver')

    # ============================================================
    # Relations
    # ============================================================
    step_ids = fields.One2many(
        'dcg.approval.request.step',
        'request_id',
        string='Steps',
    )
    log_ids = fields.One2many(
        'dcg.approval.log',
        'request_id',
        string='Logs',
    )
    step_count = fields.Integer(compute='_compute_counts', string='Step Count')
    log_count = fields.Integer(compute='_compute_counts', string='Log Count')

    # ============================================================
    # Permissions (compute)
    # ============================================================
    can_current_user_approve = fields.Boolean(
        compute='_compute_can_current_user_approve',
        string='Can Approve',
    )
    can_current_user_cancel = fields.Boolean(
        compute='_compute_can_current_user_cancel',
        string='Can Cancel',
    )

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('res_model', 'res_id', 'res_name')
    def _compute_source_ref(self):
        for rec in self:
            if rec.res_name:
                rec.source_ref = rec.res_name
            elif rec.res_model and rec.res_id:
                rec.source_ref = '%s,%s' % (rec.res_model, rec.res_id)
            else:
                rec.source_ref = False

    @api.depends('step_ids', 'log_ids')
    def _compute_counts(self):
        for rec in self:
            rec.step_count = len(rec.step_ids)
            rec.log_count = len(rec.log_ids)

    @api.depends('state', 'current_approver_user_ids')
    def _compute_can_current_user_approve(self):
        uid = self.env.uid
        for rec in self:
            rec.can_current_user_approve = (
                rec.state == 'waiting'
                and uid in rec.current_approver_user_ids.ids
            )

    @api.depends('state', 'requester_id')
    def _compute_can_current_user_cancel(self):
        is_manager = self.env.user.has_group(
            'dcg_approval_matrix.group_dcg_approval_manager'
        )
        uid = self.env.uid
        for rec in self:
            rec.can_current_user_cancel = (
                rec.state in ('draft', 'waiting', 'rejected')
                and (is_manager or rec.requester_id.id == uid)
            )

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.approval.request')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancelled'):
                raise UserError(_(
                    "You cannot delete approval request '%s' in state '%s'."
                    " Cancel it first."
                ) % (rec.display_name, rec.state))
        return super().unlink()

    # ============================================================
    # Helpers
    # ============================================================
    def _get_source_record(self):
        """Trả về document nguồn (singleton hoặc empty recordset)."""
        self.ensure_one()
        if not self.res_model or not self.res_id:
            return self.env['res.users'].browse()  # empty placeholder
        if self.res_model not in self.env:
            return self.env['res.users'].browse()
        Model = self.env[self.res_model]
        rec = Model.browse(self.res_id).exists()
        return rec

    def _add_log(self, action, note=None, step=None, from_state=None, to_state=None):
        self.ensure_one()
        self.env['dcg.approval.log'].create({
            'request_id': self.id,
            'sequence': len(self.log_ids) + 1,
            'step_no': step.sequence if step else self.current_step or 0,
            'matrix_line_id': step.matrix_line_id.id if step and step.matrix_line_id else False,
            'request_step_id': step.id if step else False,
            'approver_id': self.env.uid,
            'action': action,
            'action_date': fields.Datetime.now(),
            'from_state': from_state,
            'to_state': to_state,
            'note': note,
        })

    def _check_user_can_approve(self):
        self.ensure_one()
        if self.state != 'waiting':
            raise UserError(_(
                "Request '%(name)s' is not waiting for approval (current state: %(state)s)."
            ) % {'name': self.display_name, 'state': self.state})
        if self.env.uid not in self.current_approver_user_ids.ids:
            raise UserError(_(
                "You are not a current approver of request '%s'."
            ) % self.display_name)

    def _check_user_can_cancel(self):
        self.ensure_one()
        if self.state not in ('draft', 'waiting', 'rejected'):
            raise UserError(_(
                "Request '%(name)s' cannot be cancelled in state '%(state)s'."
            ) % {'name': self.display_name, 'state': self.state})
        is_manager = self.env.user.has_group(
            'dcg_approval_matrix.group_dcg_approval_manager'
        )
        if not is_manager and self.requester_id.id != self.env.uid:
            raise UserError(_(
                "Only the requester or an Approval Manager can cancel this request."
            ))

    def _activate_step(self, step):
        """Đặt step làm current step và tạo activity cho candidate approver."""
        self.ensure_one()
        step.write({'state': 'pending'})
        self.write({
            'current_step': step.sequence,
            'current_step_id': step.id,
            'current_line_id': step.matrix_line_id.id if step.matrix_line_id else False,
            'current_approver_user_ids': [(6, 0, step.approver_user_ids.ids)],
        })
        self._create_activities_for_current_step()

    def _create_activities_for_current_step(self):
        self.ensure_one()
        if not self.current_approver_user_ids:
            return
        try:
            activity_type = self.env.ref('mail.mail_activity_data_todo')
        except ValueError:
            return
        model = self.env['ir.model']._get('dcg.approval.request')
        summary = _('Approval required: %s') % self.name
        body = _(
            'Approval Type: %(t)s\nRequester: %(r)s\nAmount: %(a)s\nDocument: %(d)s'
        ) % {
            't': dict(self._fields['approval_type'].selection).get(self.approval_type, ''),
            'r': self.requester_id.display_name,
            'a': self.amount_total,
            'd': self.res_name or '%s,%s' % (self.res_model, self.res_id),
        }
        Activity = self.env['mail.activity'].sudo()
        for user in self.current_approver_user_ids:
            Activity.create({
                'res_model_id': model.id,
                'res_id': self.id,
                'activity_type_id': activity_type.id,
                'summary': summary,
                'note': body,
                'user_id': user.id,
                'date_deadline': fields.Date.today(),
            })

    def _close_open_activities(self):
        """Mark done tất cả activity đang mở của request."""
        self.ensure_one()
        Activity = self.env['mail.activity'].sudo()
        model = self.env['ir.model']._get('dcg.approval.request')
        activities = Activity.search([
            ('res_model_id', '=', model.id),
            ('res_id', '=', self.id),
        ])
        # Use action_done where possible, else unlink to clean up
        for act in activities:
            try:
                act.action_done()
            except Exception:
                act.unlink()

    def _find_next_pending_step(self, after_sequence):
        self.ensure_one()
        return self.step_ids.filtered(
            lambda s: s.state == 'pending' and s.sequence > after_sequence
        ).sorted(key=lambda s: (s.sequence, s.id))[:1]

    def _finish_approved(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approved_date': fields.Datetime.now(),
            'current_approver_user_ids': [(5, 0, 0)],
            'final_approver_id': self.env.uid,
            'last_action_by': self.env.uid,
            'last_action_date': fields.Datetime.now(),
        })
        self._close_open_activities()
        # Callback to source document
        src = self._get_source_record()
        if src and hasattr(src, '_approval_approved_callback'):
            src._approval_approved_callback(self)

    # ============================================================
    # Actions
    # ============================================================
    def action_approve(self):
        for rec in self:
            rec._check_user_can_approve()
            step = rec.current_step_id
            if not step:
                raise UserError(_(
                    "Request '%s' has no current step to approve."
                ) % rec.display_name)
            from_state = rec.state
            step.write({
                'state': 'approved',
                'approved_by': self.env.uid,
                'approved_date': fields.Datetime.now(),
            })
            rec._add_log(
                action='approve',
                step=step,
                from_state=from_state,
                to_state='waiting',
            )
            rec._close_open_activities()
            next_step = rec._find_next_pending_step(after_sequence=step.sequence)
            if next_step:
                rec.write({
                    'last_action_by': self.env.uid,
                    'last_action_date': fields.Datetime.now(),
                })
                rec._activate_step(next_step)
            else:
                rec._finish_approved()
        return True

    def action_open_reject_wizard(self):
        self.ensure_one()
        self._check_user_can_approve()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Approval'),
            'res_model': 'dcg.approval.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }

    def action_reject(self, reason):
        for rec in self:
            rec._check_user_can_approve()
            if not reason or not reason.strip():
                raise UserError(_("A reason is required to reject an approval request."))
            from_state = rec.state
            current = rec.current_step_id
            if current:
                current.write({
                    'state': 'rejected',
                    'rejected_by': self.env.uid,
                    'rejected_date': fields.Datetime.now(),
                    'note': reason,
                })
            # cancel remaining pending steps
            rec.step_ids.filtered(
                lambda s: s.state == 'pending' and s.sequence > (current.sequence if current else 0)
            ).write({'state': 'cancelled'})
            rec.write({
                'state': 'rejected',
                'rejected_date': fields.Datetime.now(),
                'reject_reason': reason,
                'current_approver_user_ids': [(5, 0, 0)],
                'last_action_by': self.env.uid,
                'last_action_date': fields.Datetime.now(),
            })
            rec._add_log(
                action='reject',
                step=current,
                note=reason,
                from_state=from_state,
                to_state='rejected',
            )
            rec._close_open_activities()
            src = rec._get_source_record()
            if src and hasattr(src, '_approval_rejected_callback'):
                src._approval_rejected_callback(rec)
        return True

    def action_open_cancel_wizard(self):
        self.ensure_one()
        self._check_user_can_cancel()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancel Approval'),
            'res_model': 'dcg.approval.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }

    def action_cancel(self, reason=None):
        for rec in self:
            rec._check_user_can_cancel()
            from_state = rec.state
            rec.step_ids.filtered(
                lambda s: s.state == 'pending'
            ).write({'state': 'cancelled'})
            rec.write({
                'state': 'cancelled',
                'cancelled_date': fields.Datetime.now(),
                'cancel_reason': reason,
                'current_approver_user_ids': [(5, 0, 0)],
                'last_action_by': self.env.uid,
                'last_action_date': fields.Datetime.now(),
            })
            rec._add_log(
                action='cancel',
                note=reason,
                from_state=from_state,
                to_state='cancelled',
            )
            rec._close_open_activities()
            src = rec._get_source_record()
            if src and hasattr(src, '_approval_cancelled_callback'):
                src._approval_cancelled_callback(rec)
        return True

    def action_open_source_document(self):
        self.ensure_one()
        src = self._get_source_record()
        if not src or not src.exists():
            raise UserError(_("Source document no longer exists."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Logs'),
            'res_model': 'dcg.approval.log',
            'view_mode': 'list,form',
            'domain': [('request_id', '=', self.id)],
        }
