# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


CONTRACT_TYPE_SELECTION = [
    ('implementation', 'Implementation Contract'),
    ('support', 'Support/Maintenance Contract'),
    ('training', 'Training Contract'),
    ('consulting', 'Consulting Contract'),
    ('license', 'License Contract'),
    ('other', 'Other'),
]

CONTRACT_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('waiting_approval', 'Waiting Approval'),
    ('approved', 'Approved'),
    ('active', 'Active'),
    ('in_progress', 'In Progress'),
    ('done', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('closed', 'Closed'),
]


class DcgContract(models.Model):
    _name = 'dcg.contract'
    _description = 'Customer Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'dcg.approval.mixin']
    _order = 'sign_date desc, id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Contract Number',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
    )
    contract_code = fields.Char(string='Internal Code', index=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company, tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True, default=lambda self: self.env.company.currency_id,
    )

    # ============================================================
    # Partner / source
    # ============================================================
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True, tracking=True, index=True,
    )
    lead_id = fields.Many2one('crm.lead', string='Opportunity', tracking=True)
    quotation_id = fields.Many2one('sale.order', string='Quotation', tracking=True)
    estimate_id = fields.Many2one('dcg.crm.estimate', string='Source Estimate')
    account_manager_id = fields.Many2one('res.users', string='Account Manager', tracking=True)
    presales_owner_id = fields.Many2one('res.users', string='Presales Owner')
    project_manager_id = fields.Many2one('res.users', string='Project Manager', tracking=True)
    delivery_owner_id = fields.Many2one('res.users', string='Delivery Owner', tracking=True)

    # ============================================================
    # Classification
    # ============================================================
    contract_type = fields.Selection(
        selection=CONTRACT_TYPE_SELECTION,
        string='Contract Type',
        default='implementation',
        tracking=True,
    )

    # ============================================================
    # Timeline
    # ============================================================
    sign_date = fields.Date(string='Signed Date', tracking=True)
    effective_date = fields.Date(string='Effective Date', tracking=True)
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    warranty_end_date = fields.Date(string='Warranty End Date')

    # ============================================================
    # Commercial / finance
    # ============================================================
    amount_untaxed = fields.Monetary(string='Amount Untaxed', currency_field='currency_id', tracking=True)
    tax_amount = fields.Monetary(string='Tax Amount', currency_field='currency_id')
    amount_total = fields.Monetary(string='Total Amount', currency_field='currency_id', tracking=True)
    expected_cost = fields.Monetary(string='Expected Cost', currency_field='currency_id')
    expected_margin = fields.Monetary(
        string='Expected Margin', currency_field='currency_id',
        compute='_compute_expected_margin', store=True,
    )
    expected_margin_rate = fields.Float(
        string='Margin Rate (%)',
        compute='_compute_expected_margin', store=True,
    )
    line_amount_total = fields.Monetary(
        string='Lines Total', currency_field='currency_id',
        compute='_compute_line_amount_total', store=True,
    )
    payment_term_note = fields.Html(string='Payment Terms')
    billing_note = fields.Text(string='Billing Note')

    # ============================================================
    # State
    # ============================================================
    state = fields.Selection(
        selection=CONTRACT_STATE_SELECTION,
        string='Status', default='draft', required=True,
        tracking=True, index=True,
    )

    # ============================================================
    # Content / legal
    # ============================================================
    contract_summary = fields.Html(string='Contract Summary')
    scope_summary = fields.Html(string='Scope Summary')
    assumption_note = fields.Html(string='Assumptions')
    exclusion_note = fields.Html(string='Exclusions')
    legal_note = fields.Html(string='Legal Note')
    handover_note = fields.Html(string='Handover Note')
    internal_note = fields.Text(string='Internal Note')

    # ============================================================
    # Relations
    # ============================================================
    line_ids = fields.One2many('dcg.contract.line', 'contract_id', string='Contract Lines', copy=True)
    payment_ids = fields.One2many('dcg.contract.payment', 'contract_id', string='Payment Schedule', copy=True)
    appendix_ids = fields.One2many('dcg.contract.appendix', 'contract_id', string='Appendices')
    acceptance_ids = fields.One2many('dcg.contract.acceptance', 'contract_id', string='Acceptances')

    line_count = fields.Integer(compute='_compute_counts')
    payment_count = fields.Integer(compute='_compute_counts')
    appendix_count = fields.Integer(compute='_compute_counts')
    acceptance_count = fields.Integer(compute='_compute_counts')

    # ============================================================
    # Handover
    # ============================================================
    handover_completed = fields.Boolean(string='Handover Completed')
    handover_date = fields.Date(string='Handover Date')

    # ============================================================
    # Attachments
    # ============================================================
    signed_attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_contract_signed_attachment_rel',
        'contract_id', 'attachment_id', string='Signed Documents',
    )
    draft_attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_contract_draft_attachment_rel',
        'contract_id', 'attachment_id', string='Draft Documents',
    )

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('amount_total', 'expected_cost')
    def _compute_expected_margin(self):
        for rec in self:
            rec.expected_margin = (rec.amount_total or 0.0) - (rec.expected_cost or 0.0)
            rec.expected_margin_rate = (
                (rec.expected_margin / rec.amount_total * 100.0)
                if rec.amount_total else 0.0
            )

    @api.depends('line_ids.amount')
    def _compute_line_amount_total(self):
        for rec in self:
            rec.line_amount_total = sum(rec.line_ids.mapped('amount'))

    def _compute_counts(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
            rec.payment_count = len(rec.payment_ids)
            rec.appendix_count = len(rec.appendix_ids)
            rec.acceptance_count = len(rec.acceptance_ids)

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.contract')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancelled'):
                raise UserError(_(
                    "Cannot delete contract '%s' in state '%s'. Cancel it first."
                ) % (rec.display_name, rec.state))
        return super().unlink()

    # ============================================================
    # Approval mixin overrides
    # ============================================================
    def _get_approval_type(self):
        self.ensure_one()
        return 'contract_approval'

    def _get_approval_amount(self):
        self.ensure_one()
        return self.amount_total or 0.0

    def _validate_before_submit_approval(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Contract must have a customer before submitting for approval."))
        if not self.line_ids:
            raise UserError(_("Contract must have at least one line item before submitting for approval."))
        if not (self.amount_total or 0.0) > 0:
            raise UserError(_("Contract total amount must be greater than 0."))
        return True

    def _approval_approved_callback(self, request):
        self.ensure_one()
        super()._approval_approved_callback(request)
        self.write({'state': 'approved'})

    def _approval_rejected_callback(self, request):
        self.ensure_one()
        super()._approval_rejected_callback(request)
        self.write({'state': 'draft'})

    def _approval_cancelled_callback(self, request):
        self.ensure_one()
        super()._approval_cancelled_callback(request)
        self.write({'state': 'draft'})

    # ============================================================
    # State actions
    # ============================================================
    def action_submit_approval(self):
        for rec in self:
            rec.state = 'waiting_approval'
        return super().action_submit_approval()

    def action_activate_contract(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Contract must be approved before activation."))
            rec.write({'state': 'active'})
        return True

    def action_mark_in_progress(self):
        for rec in self:
            if rec.state != 'active':
                raise UserError(_("Contract must be active before marking in progress."))
            rec.write({'state': 'in_progress'})
        return True

    def action_mark_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_("Contract must be in progress before marking as done."))
            rec.write({'state': 'done'})
        return True

    def action_open_close_wizard(self):
        self.ensure_one()
        if self.state != 'done':
            raise UserError(_("Contract must be completed (done) before closing."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Close Contract'),
            'res_model': 'dcg.contract.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def action_cancel_contract(self):
        for rec in self:
            if rec.state in ('closed',):
                raise UserError(_("Closed contract cannot be cancelled."))
            rec.write({'state': 'cancelled'})
        return True

    # ============================================================
    # Related actions
    # ============================================================
    def action_create_appendix(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Appendix'),
            'res_model': 'dcg.contract.appendix',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_contract_id': self.id,
                'default_old_amount_total': self.amount_total,
                'default_old_end_date': self.end_date,
                'default_currency_id': self.currency_id.id,
            },
        }

    def action_create_acceptance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Acceptance'),
            'res_model': 'dcg.contract.acceptance',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_contract_id': self.id,
            },
        }

    def action_view_appendices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Appendices'),
            'res_model': 'dcg.contract.appendix',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_acceptances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Acceptances'),
            'res_model': 'dcg.contract.acceptance',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Schedule'),
            'res_model': 'dcg.contract.payment',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }
