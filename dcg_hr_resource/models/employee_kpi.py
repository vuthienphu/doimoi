# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgEmployeeKpi(models.Model):
    _name = 'dcg.employee.kpi'
    _description = 'Employee Delivery KPI'
    _order = 'period desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', index=True,
    )
    period = fields.Char(string='Period', required=True)
    period_start = fields.Date(string='Period Start')
    period_end = fields.Date(string='Period End')

    # Metrics
    utilization_rate = fields.Float(string='Utilization (%)')
    billable_rate = fields.Float(string='Billable (%)')
    total_hours = fields.Float(string='Total Hours')
    billable_hours = fields.Float(string='Billable Hours')
    overtime_hours = fields.Float(string='OT Hours')
    project_count = fields.Integer(string='Projects')
    ticket_resolved = fields.Integer(string='Tickets Resolved')

    # Scores
    customer_score = fields.Float(string='Customer Score')
    manager_score = fields.Float(string='Manager Score')
    overall_score = fields.Float(string='Overall Score')

    is_locked = fields.Boolean(string='Locked')
    note = fields.Text(string='Note')
