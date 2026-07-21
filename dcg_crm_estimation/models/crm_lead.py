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
    work_estimation_ids = fields.One2many('crm.lead.work.estimation', 'lead_id', string='Công việc ước tính')
    value_estimation_ids = fields.One2many('crm.lead.value.estimation', 'lead_id', string='Chi phí ngoài nhân sự')
    
    total_effort = fields.Float(
        string='Tổng Effort (MD)',
        compute='_compute_estimation_totals',
        store=True,
    )
    estimated_human_cost = fields.Monetary(
        string='Giá vốn nhân sự',
        compute='_compute_estimation_totals',
        store=True,
        currency_field='currency_id',
    )
    estimated_other_cost = fields.Monetary(
        string='Giá vốn ngoài nhân sự',
        compute='_compute_estimation_totals',
        store=True,
        currency_field='currency_id',
    )
    total_estimated_cost = fields.Monetary(
        string='Tổng giá vốn',
        compute='_compute_estimation_totals',
        store=True,
        currency_field='currency_id',
    )
    estimated_profit = fields.Monetary(
        string='Lợi nhuận ước tính',
        compute='_compute_estimation_totals',
        store=True,
        currency_field='currency_id',
    )
    estimated_margin = fields.Float(
        string='Tỷ suất lợi nhuận (%)',
        compute='_compute_estimation_totals',
        store=True,
    )

    @api.depends(
        'work_estimation_ids.ba_md', 'work_estimation_ids.backend_md', 'work_estimation_ids.frontend_md',
        'work_estimation_ids.qa_md', 'work_estimation_ids.devops_md', 'work_estimation_ids.uiux_md',
        'value_estimation_ids.subtotal', 'expected_revenue'
    )
    def _compute_estimation_totals(self):
        RoleCost = self.env['crm.role.cost']
        today = fields.Date.context_today(self)
        for lead in self:
            # 1. Total effort
            lead.total_effort = sum(lead.work_estimation_ids.mapped('total_md'))

            # 2. Human cost: Fetch active role costs and convert to lead's currency
            role_costs = RoleCost.search([('active', '=', True)])
            cost_map = {}
            for rc in role_costs:
                cost_in_lead_currency = rc.currency_id._convert(
                    rc.cost_per_md, lead.currency_id, lead.company_id, today
                )
                cost_map[rc.role] = cost_in_lead_currency

            human_cost = 0.0
            for line in lead.work_estimation_ids:
                human_cost += (
                    line.ba_md * cost_map.get('ba', 0.0) +
                    line.backend_md * cost_map.get('backend', 0.0) +
                    line.frontend_md * cost_map.get('frontend', 0.0) +
                    line.qa_md * cost_map.get('qa', 0.0) +
                    line.devops_md * cost_map.get('devops', 0.0) +
                    line.uiux_md * cost_map.get('uiux', 0.0)
                )
            lead.estimated_human_cost = human_cost

            # 3. Other cost
            lead.estimated_other_cost = sum(lead.value_estimation_ids.mapped('subtotal'))

            # 4. Total estimated cost
            lead.total_estimated_cost = lead.estimated_human_cost + lead.estimated_other_cost

            # 5. Profit
            lead.estimated_profit = lead.expected_revenue - lead.total_estimated_cost

            # 6. Margin
            if lead.expected_revenue:
                lead.estimated_margin = (lead.estimated_profit / lead.expected_revenue) * 100.0
            else:
                lead.estimated_margin = 0.0
