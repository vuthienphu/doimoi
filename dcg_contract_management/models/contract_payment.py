# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


PAYMENT_TYPE_SELECTION = [
    ('percent', 'By Percentage'),
    ('fixed', 'Fixed Amount'),
]

PAYMENT_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('waiting', 'Waiting'),
    ('partial', 'Partially Received'),
    ('paid', 'Paid'),
    ('cancelled', 'Cancelled'),
]


class DcgContractPayment(models.Model):
    _name = 'dcg.contract.payment'
    _description = 'Contract Payment Schedule'
    _inherit = ['mail.thread']
    _order = 'sequence, due_date, id'

    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer(string='Installment', default=10)
    name = fields.Char(string='Milestone', required=True)
    milestone_name = fields.Char(string='Milestone Detail')

    # Payment value
    currency_id = fields.Many2one(related='contract_id.currency_id', string='Currency', readonly=True)
    payment_type = fields.Selection(
        selection=PAYMENT_TYPE_SELECTION, string='Payment Type',
        required=True, default='percent',
    )
    percent = fields.Float(string='Percentage (%)')
    amount = fields.Monetary(
        string='Amount', currency_field='currency_id',
        compute='_compute_amount', store=True, readonly=False,
    )
    amount_received = fields.Monetary(string='Amount Received', currency_field='currency_id', tracking=True)
    balance_amount = fields.Monetary(
        string='Balance', currency_field='currency_id',
        compute='_compute_balance', store=True,
    )

    # Timing
    due_date = fields.Date(string='Due Date')
    planned_invoice_date = fields.Date(string='Planned Invoice Date')
    actual_received_date = fields.Date(string='Actual Received Date')
    condition_note = fields.Html(string='Payment Condition')

    # State
    state = fields.Selection(
        selection=PAYMENT_STATE_SELECTION, string='Status',
        default='draft', tracking=True,
    )
    invoice_note = fields.Text(string='Invoice Note')

    @api.depends('payment_type', 'percent', 'contract_id.amount_total')
    def _compute_amount(self):
        for rec in self:
            if rec.payment_type == 'percent' and rec.contract_id:
                rec.amount = (rec.contract_id.amount_total or 0.0) * (rec.percent or 0.0) / 100.0
            # fixed: amount stays as manually entered (readonly=False)

    @api.depends('amount', 'amount_received')
    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = (rec.amount or 0.0) - (rec.amount_received or 0.0)

    def action_mark_waiting(self):
        self.write({'state': 'waiting'})

    def action_mark_partial(self):
        for rec in self:
            if not rec.amount_received:
                raise UserError(_("Please enter the received amount before marking as partial."))
            rec.state = 'partial'

    def action_mark_paid(self):
        for rec in self:
            rec.write({
                'state': 'paid',
                'actual_received_date': rec.actual_received_date or fields.Date.today(),
            })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
