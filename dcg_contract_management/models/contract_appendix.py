# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


APPENDIX_TYPE_SELECTION = [
    ('scope_change', 'Scope Change'),
    ('value_change', 'Value Change'),
    ('timeline_extension', 'Timeline Extension'),
    ('general_update', 'General Update'),
]

APPENDIX_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('waiting_approval', 'Waiting Approval'),
    ('approved', 'Approved'),
    ('effective', 'Effective'),
    ('cancelled', 'Cancelled'),
]


class DcgContractAppendix(models.Model):
    _name = 'dcg.contract.appendix'
    _description = 'Contract Appendix'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'dcg.approval.mixin']
    _order = 'appendix_date desc, id desc'

    # ============================================================
    # Header
    # ============================================================
    name = fields.Char(
        string='Appendix Number', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True,
        ondelete='restrict', index=True, tracking=True,
    )
    partner_id = fields.Many2one(related='contract_id.partner_id', store=True, string='Customer')
    appendix_type = fields.Selection(
        selection=APPENDIX_TYPE_SELECTION, string='Appendix Type',
        required=True, tracking=True,
    )
    appendix_date = fields.Date(string='Appendix Date', tracking=True)
    effective_date = fields.Date(string='Effective Date')
    state = fields.Selection(
        selection=APPENDIX_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True, index=True,
    )
    currency_id = fields.Many2one(
        related='contract_id.currency_id', string='Currency', readonly=True,
    )

    # ============================================================
    # Impact
    # ============================================================
    value_delta = fields.Monetary(string='Value Change', currency_field='currency_id', tracking=True)
    old_amount_total = fields.Monetary(string='Amount Before', currency_field='currency_id')
    new_amount_total = fields.Monetary(
        string='Amount After', currency_field='currency_id',
        compute='_compute_new_amount', store=True,
    )
    old_end_date = fields.Date(string='End Date Before')
    new_end_date = fields.Date(string='New End Date')

    reason = fields.Html(string='Reason')
    summary = fields.Html(string='Summary')

    # ============================================================
    # Lines
    # ============================================================
    line_ids = fields.One2many(
        'dcg.contract.appendix.line', 'appendix_id', string='Change Lines', copy=True,
    )
    line_count = fields.Integer(compute='_compute_line_count')

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('old_amount_total', 'value_delta')
    def _compute_new_amount(self):
        for rec in self:
            rec.new_amount_total = (rec.old_amount_total or 0.0) + (rec.value_delta or 0.0)

    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.contract.appendix')
                vals['name'] = seq or _('New')
            # snapshot old values from contract
            if vals.get('contract_id') and not vals.get('old_amount_total'):
                contract = self.env['dcg.contract'].browse(vals['contract_id'])
                vals.setdefault('old_amount_total', contract.amount_total)
                vals.setdefault('old_end_date', contract.end_date)
        return super().create(vals_list)

    # ============================================================
    # Approval mixin overrides
    # ============================================================
    def _get_approval_type(self):
        self.ensure_one()
        return 'appendix_approval'

    def _get_approval_amount(self):
        self.ensure_one()
        return abs(self.value_delta or 0.0)

    def _validate_before_submit_approval(self):
        self.ensure_one()
        if not self.contract_id:
            raise UserError(_("Appendix must be linked to a contract."))
        return True

    def _approval_approved_callback(self, request):
        self.ensure_one()
        super()._approval_approved_callback(request)
        self.write({'state': 'approved'})

    def _approval_rejected_callback(self, request):
        self.ensure_one()
        super()._approval_rejected_callback(request)
        self.write({'state': 'draft'})

    # ============================================================
    # State actions
    # ============================================================
    def action_submit_approval(self):
        for rec in self:
            rec.state = 'waiting_approval'
        return super().action_submit_approval()

    def action_mark_effective(self):
        """Đặt appendix hiệu lực và áp dụng thay đổi lên contract."""
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Appendix must be approved before marking as effective."))
            rec._apply_appendix_to_contract()
            rec.write({
                'state': 'effective',
                'effective_date': rec.effective_date or fields.Date.today(),
            })
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == 'effective':
                raise UserError(_("Cannot cancel an effective appendix. Create a reversal appendix instead."))
            rec.write({'state': 'cancelled'})
        return True

    # ============================================================
    # Apply changes to parent contract
    # ============================================================
    def _apply_appendix_to_contract(self):
        """Cập nhật contract khi appendix effective (spec mục 47, 52, 93)."""
        self.ensure_one()
        contract = self.contract_id
        vals = {}
        if self.value_delta:
            vals['amount_total'] = (contract.amount_total or 0.0) + self.value_delta
            vals['amount_untaxed'] = (contract.amount_untaxed or 0.0) + self.value_delta
        if self.new_end_date:
            vals['end_date'] = self.new_end_date
        if vals:
            contract.write(vals)

        # Create contract lines from appendix lines with change_type = 'add'
        ContractLine = self.env['dcg.contract.line']
        for aline in self.line_ids.filtered(lambda l: l.change_type == 'add'):
            ContractLine.create({
                'contract_id': contract.id,
                'name': aline.name,
                'quantity': aline.quantity or 1.0,
                'unit_price': aline.unit_price or 0.0,
                'description': aline.description,
                'planned_start_date': aline.planned_start_date,
                'planned_end_date': aline.planned_end_date,
                'note': _('Added by appendix %s') % self.name,
            })
