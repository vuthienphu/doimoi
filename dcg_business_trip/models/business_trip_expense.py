# -*- coding: utf-8 -*-
from odoo import api, fields, models


EXPENSE_CATEGORY_SELECTION = [
    ('transport', 'Transport'),
    ('hotel', 'Hotel'),
    ('allowance', 'Allowance'),
    ('meal', 'Meal'),
    ('entertainment', 'Entertainment'),
    ('visa', 'Visa / Documents'),
    ('other', 'Other'),
]

EXPENSE_SOURCE_SELECTION = [
    ('estimated', 'Estimated'),
    ('actual', 'Actual'),
    ('adjustment', 'Adjustment'),
]


class DcgBusinessTripExpense(models.Model):
    _name = 'dcg.business.trip.expense'
    _description = 'Business Trip Expense'
    _order = 'expense_date desc, id desc'

    trip_id = fields.Many2one(
        'dcg.business.trip', string='Trip', required=True,
        ondelete='cascade', index=True,
    )
    project_id = fields.Many2one(
        related='trip_id.project_id', string='Project', store=True,
    )
    contract_id = fields.Many2one(
        related='trip_id.contract_id', string='Contract', store=True,
    )
    finance_id = fields.Many2one(
        related='trip_id.finance_id', string='Finance', store=True,
    )
    member_id = fields.Many2one(
        'dcg.business.trip.member', string='Member',
        domain="[('trip_id', '=', trip_id)]",
    )

    # Classification
    name = fields.Char(string='Description', required=True)
    expense_type_id = fields.Many2one('dcg.expense.type', string='Expense Type')
    expense_category = fields.Selection(
        selection=EXPENSE_CATEGORY_SELECTION, string='Category',
        required=True, default='transport',
    )
    source_type = fields.Selection(
        selection=EXPENSE_SOURCE_SELECTION, string='Source',
        required=True, default='actual',
    )
    description = fields.Text(string='Detail')

    # Value
    expense_date = fields.Date(string='Date', default=fields.Date.context_today)
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        related='trip_id.currency_id', string='Currency', store=True,
    )

    # Attachments
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_trip_expense_attachment_rel',
        'expense_id', 'attachment_id', string='Receipts',
    )
    bill_reference = fields.Char(string='Bill Reference')
    vendor_name = fields.Char(string='Vendor')
    note = fields.Text(string='Note')

    # Finance sync trace (spec mục 81-82)
    finance_cost_line_id = fields.Many2one(
        'dcg.project.finance.cost.line', string='Finance Cost Line',
        readonly=True, copy=False,
    )
    finance_synced = fields.Boolean(string='Synced to Finance', copy=False)
