# -*- coding: utf-8 -*-
from odoo import fields, models


CHANGE_TYPE_SELECTION = [
    ('add', 'Add New Scope'),
    ('update', 'Update Existing Scope'),
    ('remove', 'Remove Scope'),
]


class DcgContractAppendixLine(models.Model):
    _name = 'dcg.contract.appendix.line'
    _description = 'Contract Appendix Line'
    _order = 'sequence, id'

    appendix_id = fields.Many2one(
        'dcg.contract.appendix', string='Appendix', required=True, ondelete='cascade', index=True,
    )
    contract_id = fields.Many2one(related='appendix_id.contract_id', store=True, string='Contract')
    contract_line_id = fields.Many2one(
        'dcg.contract.line', string='Affected Contract Line',
        domain="[('contract_id', '=', contract_id)]",
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Description', required=True)
    change_type = fields.Selection(
        selection=CHANGE_TYPE_SELECTION, string='Change Type', required=True, default='add',
    )
    description = fields.Html(string='Detail')

    # Value / timeline
    currency_id = fields.Many2one(related='appendix_id.currency_id', string='Currency', readonly=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    amount_delta = fields.Monetary(string='Amount Delta', currency_field='currency_id')
    planned_start_date = fields.Date(string='Planned Start')
    planned_end_date = fields.Date(string='Planned End')
    note = fields.Text(string='Note')
