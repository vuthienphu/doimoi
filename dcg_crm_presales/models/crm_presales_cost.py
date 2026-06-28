# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


PRESALES_COST_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
]


class DcgCrmPresalesCost(models.Model):
    """Chi phí phát sinh trong giai đoạn presales (khảo sát, demo, đi lại...)."""
    _name = 'dcg.crm.presales.cost'
    _description = 'CRM Presales Cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expense_date desc, id desc'

    name = fields.Char(
        string='Description',
        required=True,
        default=lambda self: _('New'),
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        required=True,
        ondelete='cascade',
        index=True,
        domain="[('type', '=', 'opportunity')]",
    )
    partner_id = fields.Many2one(
        related='lead_id.partner_id',
        string='Customer',
        store=True,
        readonly=True,
    )
    expense_type_id = fields.Many2one(
        'dcg.expense.type',
        string='Expense Type',
        required=True,
    )
    expense_date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )
    description = fields.Text(string='Description')
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    billable_to_customer = fields.Boolean(
        string='Billable to Customer',
        help='Whether this presales cost can be charged to the customer as part of the deal.',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'dcg_crm_presales_cost_attachment_rel',
        'cost_id',
        'attachment_id',
        string='Attachments / Receipts',
    )
    state = fields.Selection(
        selection=PRESALES_COST_STATE_SELECTION,
        string='Status',
        default='draft',
        tracking=True,
    )

    # ============================================================
    # Onchange
    # ============================================================
    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id and self.lead_id.company_id:
            self.currency_id = self.lead_id.company_id.currency_id

    # ============================================================
    # Actions
    # ============================================================
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True
