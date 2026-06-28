# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Delivery profile
    employee_code = fields.Char(string='Employee Code')
    career_level_id = fields.Many2one(
        'dcg.employee.career.level', string='Career Level',
    )
    is_billable = fields.Boolean(string='Billable Resource', default=True)
    join_delivery_date = fields.Date(string='Delivery Join Date')
    hour_cost = fields.Monetary(
        string='Hour Cost', currency_field='currency_id',
        help='Internal cost rate per hour. Overrides role default.',
    )
    hour_bill_rate = fields.Monetary(
        string='Hour Bill Rate', currency_field='currency_id',
        help='Billing rate per hour. Overrides role default.',
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id', store=True,
    )
    capacity_hours_month = fields.Float(
        string='Monthly Capacity (h)', default=160.0,
    )
    target_utilization = fields.Float(
        string='Target Utilization (%)', default=75.0,
    )

    # Relations
    certificate_ids = fields.One2many(
        'dcg.employee.certificate', 'employee_id', string='Certificates',
    )
    training_ids = fields.One2many(
        'dcg.employee.training', 'employee_id', string='Trainings',
    )
    competency_ids = fields.One2many(
        'dcg.employee.competency', 'employee_id', string='Competency Assessments',
    )
    kpi_ids = fields.One2many(
        'dcg.employee.kpi', 'employee_id', string='KPIs',
    )
    availability_ids = fields.One2many(
        'dcg.employee.availability', 'employee_id', string='Availability',
    )

    certificate_count = fields.Integer(compute='_compute_hr_resource_counts')
    training_count = fields.Integer(compute='_compute_hr_resource_counts')

    def _compute_hr_resource_counts(self):
        for emp in self:
            emp.certificate_count = len(emp.certificate_ids)
            emp.training_count = len(emp.training_ids)
