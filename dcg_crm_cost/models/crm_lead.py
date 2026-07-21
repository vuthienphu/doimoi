# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='company_id.currency_id',
        readonly=True,
    )
    cost_ids = fields.One2many('crm.lead.cost', 'lead_id', string='Chi phí thực tế')
    total_cost = fields.Monetary(
        string='Tổng chi phí',
        compute='_compute_cost_totals',
        store=True,
        currency_field='currency_id',
    )
    profit_loss = fields.Monetary(
        string='Lãi/Lỗ',
        compute='_compute_cost_totals',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('cost_ids.amount', 'expected_revenue')
    def _compute_cost_totals(self):
        for lead in self:
            lead.total_cost = sum(lead.cost_ids.mapped('amount'))
            lead.profit_loss = lead.expected_revenue - lead.total_cost
