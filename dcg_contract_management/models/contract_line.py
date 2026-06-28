# -*- coding: utf-8 -*-
from odoo import api, fields, models


LINE_TYPE_SELECTION = [
    ('implementation', 'Implementation'),
    ('support', 'Support'),
    ('training', 'Training'),
    ('consulting', 'Consulting'),
    ('license', 'License'),
    ('other', 'Other'),
]


class DcgContractLine(models.Model):
    _name = 'dcg.contract.line'
    _description = 'Contract Line'
    _order = 'sequence, id'

    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Description', required=True)
    service_catalog_id = fields.Many2one('dcg.service.catalog', string='Service')
    scope_id = fields.Many2one('dcg.crm.solution.scope', string='Source Scope')
    estimate_line_id = fields.Many2one('dcg.crm.estimate.line', string='Source Estimate Line')
    line_type = fields.Selection(selection=LINE_TYPE_SELECTION, string='Type', default='implementation')
    description = fields.Html(string='Detail')

    # Commercial
    currency_id = fields.Many2one(related='contract_id.currency_id', string='Currency', readonly=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_name = fields.Char(string='Unit', default='service')
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    amount = fields.Monetary(string='Amount', currency_field='currency_id', compute='_compute_amount', store=True)
    planned_start_date = fields.Date(string='Planned Start')
    planned_end_date = fields.Date(string='Planned End')
    note = fields.Text(string='Note')

    # Effort snapshot
    ba_hours = fields.Float(string='BA Hours')
    dev_hours = fields.Float(string='Dev Hours')
    test_hours = fields.Float(string='Test Hours')
    pm_hours = fields.Float(string='PM Hours')
    support_hours = fields.Float(string='Support Hours')
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for rec in self:
            rec.amount = (rec.quantity or 1.0) * (rec.unit_price or 0.0)

    @api.depends('ba_hours', 'dev_hours', 'test_hours', 'pm_hours', 'support_hours')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = sum([
                rec.ba_hours or 0, rec.dev_hours or 0, rec.test_hours or 0,
                rec.pm_hours or 0, rec.support_hours or 0,
            ])
