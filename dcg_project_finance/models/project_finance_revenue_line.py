# -*- coding: utf-8 -*-
from odoo import api, fields, models


LINE_TYPE_SELECTION = [
    ('contract_value', 'Contract Value'),
    ('appendix_value', 'Appendix Value'),
    ('invoice', 'Invoice'),
    ('collection', 'Collection'),
    ('adjustment', 'Adjustment'),
]

REVENUE_STATE_SELECTION = [
    ('planned', 'Planned'),
    ('invoiced', 'Invoiced'),
    ('partial', 'Partially Collected'),
    ('collected', 'Collected'),
    ('cancelled', 'Cancelled'),
]


class DcgProjectFinanceRevenueLine(models.Model):
    _name = 'dcg.project.finance.revenue.line'
    _description = 'Project Finance Revenue Line'
    _order = 'revenue_date desc, id desc'

    finance_id = fields.Many2one(
        'dcg.project.finance', string='Finance Record', required=True,
        ondelete='cascade', index=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True, index=True,
    )
    contract_id = fields.Many2one('dcg.contract', string='Contract', required=True)
    payment_id = fields.Many2one('dcg.contract.payment', string='Payment Milestone')
    acceptance_id = fields.Many2one('dcg.contract.acceptance', string='Acceptance')
    milestone_id = fields.Many2one('dcg.project.milestone', string='Milestone')

    # Classification
    line_type = fields.Selection(
        selection=LINE_TYPE_SELECTION, string='Type', required=True, default='contract_value',
    )
    name = fields.Char(string='Description', required=True)
    description = fields.Text(string='Detail')

    # Value
    revenue_date = fields.Date(string='Date')
    currency_id = fields.Many2one(
        related='finance_id.currency_id', string='Currency', store=True,
    )
    planned_amount = fields.Monetary(string='Planned', currency_field='currency_id')
    invoiced_amount = fields.Monetary(string='Invoiced', currency_field='currency_id')
    collected_amount = fields.Monetary(string='Collected', currency_field='currency_id')
    balance_amount = fields.Monetary(
        string='Balance', currency_field='currency_id',
        compute='_compute_balance', store=True,
    )
    state = fields.Selection(
        selection=REVENUE_STATE_SELECTION, string='Status',
        default='planned',
    )

    @api.depends('invoiced_amount', 'collected_amount')
    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = (rec.invoiced_amount or 0) - (rec.collected_amount or 0)
