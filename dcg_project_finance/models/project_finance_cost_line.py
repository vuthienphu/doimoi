# -*- coding: utf-8 -*-
from odoo import fields, models


COST_TYPE_SELECTION = [
    ('labor', 'Labor'),
    ('travel', 'Travel'),
    ('subcontract', 'Subcontract'),
    ('license', 'License / Software'),
    ('expense', 'General Expense'),
    ('other', 'Other'),
]

SOURCE_TYPE_SELECTION = [
    ('timesheet', 'Timesheet'),
    ('trip', 'Business Trip'),
    ('manual', 'Manual'),
    ('vendor_bill', 'Vendor Bill'),
    ('expense_claim', 'Expense Claim'),
    ('other', 'Other'),
]


class DcgProjectFinanceCostLine(models.Model):
    _name = 'dcg.project.finance.cost.line'
    _description = 'Project Finance Cost Line'
    _order = 'cost_date desc, id desc'

    finance_id = fields.Many2one(
        'dcg.project.finance', string='Finance Record', required=True,
        ondelete='cascade', index=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True, index=True,
    )
    contract_id = fields.Many2one('dcg.contract', string='Contract')
    scope_id = fields.Many2one('dcg.project.scope', string='Scope')
    milestone_id = fields.Many2one('dcg.project.milestone', string='Milestone')

    # Classification
    cost_type = fields.Selection(
        selection=COST_TYPE_SELECTION, string='Cost Type', required=True, default='labor',
    )
    source_type = fields.Selection(
        selection=SOURCE_TYPE_SELECTION, string='Source', required=True, default='manual',
    )
    name = fields.Char(string='Description', required=True)
    description = fields.Text(string='Detail')

    # Value
    cost_date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')

    # Trace source
    timesheet_line_id = fields.Many2one(
        'account.analytic.line', string='Timesheet Line', index=True,
    )
    external_ref = fields.Char(string='External Reference')
