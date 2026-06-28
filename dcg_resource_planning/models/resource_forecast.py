# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgResourceForecast(models.Model):
    _name = 'dcg.resource.forecast'
    _description = 'Resource Forecast'
    _order = 'period_start, role_id'

    role_id = fields.Many2one(
        'dcg.resource.role', string='Role', required=True, index=True,
    )
    department_id = fields.Many2one('hr.department', string='Department')
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )

    # Period
    period_start = fields.Date(string='Period Start', required=True)
    period_end = fields.Date(string='Period End', required=True)
    period_label = fields.Char(
        string='Period', compute='_compute_period_label', store=True,
    )

    # Demand / supply
    demand_count = fields.Integer(
        string='Demand (FTE)',
        help='Number of FTEs needed for this role in this period.',
    )
    demand_hours = fields.Float(string='Demand (h)')
    supply_count = fields.Integer(
        string='Supply (FTE)',
        help='Number of FTEs available for this role.',
    )
    supply_hours = fields.Float(string='Supply (h)')
    gap_count = fields.Integer(
        string='Gap (FTE)', compute='_compute_gap', store=True,
    )
    gap_hours = fields.Float(
        string='Gap (h)', compute='_compute_gap', store=True,
    )

    # Source
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project',
        help='Specific project driving this demand (optional).',
    )
    note = fields.Text(string='Note')

    _sql_constraints = [
        ('role_period_project_uniq',
         'UNIQUE(role_id, period_start, project_id, company_id)',
         'Duplicate forecast entry for this role, period, and project.'),
    ]

    @api.depends('period_start')
    def _compute_period_label(self):
        for rec in self:
            rec.period_label = rec.period_start.strftime('%Y-%m') if rec.period_start else ''

    @api.depends('demand_count', 'supply_count', 'demand_hours', 'supply_hours')
    def _compute_gap(self):
        for rec in self:
            rec.gap_count = (rec.demand_count or 0) - (rec.supply_count or 0)
            rec.gap_hours = (rec.demand_hours or 0) - (rec.supply_hours or 0)
