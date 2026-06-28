# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgCrmEstimateLine(models.Model):
    """Hạng mục chi tiết effort/cost/revenue trong một estimate."""
    _name = 'dcg.crm.estimate.line'
    _description = 'CRM Estimate Line'
    _order = 'sequence, id'

    estimate_id = fields.Many2one(
        'dcg.crm.estimate',
        string='Estimate',
        required=True,
        ondelete='cascade',
        index=True,
    )
    scope_id = fields.Many2one(
        'dcg.crm.solution.scope',
        string='Scope Item',
        domain="[('lead_id', '=', lead_id)]",
    )
    lead_id = fields.Many2one(
        related='estimate_id.lead_id',
        store=True,
        string='Opportunity',
        readonly=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Line', required=True)
    service_catalog_id = fields.Many2one(
        'dcg.service.catalog',
        string='Service',
    )

    # Effort
    ba_hours = fields.Float(string='BA Hours')
    dev_hours = fields.Float(string='Dev Hours')
    test_hours = fields.Float(string='Test Hours')
    pm_hours = fields.Float(string='PM Hours')
    support_hours = fields.Float(string='Support Hours')
    other_hours = fields.Float(string='Other Hours')
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)

    # Commercial
    currency_id = fields.Many2one(
        related='estimate_id.currency_id',
        string='Currency',
        readonly=True,
    )
    cost_amount = fields.Monetary(string='Cost', currency_field='currency_id')
    revenue_amount = fields.Monetary(string='Revenue', currency_field='currency_id')
    timeline_days = fields.Integer(string='Timeline (days)')
    note = fields.Text(string='Note')

    @api.depends('ba_hours', 'dev_hours', 'test_hours', 'pm_hours', 'support_hours', 'other_hours')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = (
                (rec.ba_hours or 0.0)
                + (rec.dev_hours or 0.0)
                + (rec.test_hours or 0.0)
                + (rec.pm_hours or 0.0)
                + (rec.support_hours or 0.0)
                + (rec.other_hours or 0.0)
            )
