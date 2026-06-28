# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DcgKpiTarget(models.Model):
    _name = 'dcg.kpi.target'
    _description = 'KPI Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='KPI Name',
        required=True,
        tracking=True,
        translate=True,
    )
    target_type = fields.Selection(
        selection=[
            ('sales_revenue', 'Sales Revenue'),
            ('project_margin', 'Project Margin'),
            ('billable_rate', 'Billable Rate'),
            ('utilization_rate', 'Utilization Rate'),
            ('timesheet_compliance', 'Timesheet Compliance'),
            ('ticket_sla', 'Ticket SLA'),
            ('customer_satisfaction', 'Customer Satisfaction'),
            ('other', 'Other'),
        ],
        string='Target Type',
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
    )
    owner_id = fields.Many2one(
        'hr.employee',
        string='Owner',
        tracking=True,
    )
    period_type = fields.Selection(
        selection=[
            ('month', 'Month'),
            ('quarter', 'Quarter'),
            ('year', 'Year'),
        ],
        string='Period',
        required=True,
        default='month',
        tracking=True,
    )
    target_value = fields.Float(
        string='Target Value',
        required=True,
        tracking=True,
    )
    unit = fields.Char(
        string='Unit',
        help='Examples: %, hours, tickets, VND, etc.',
    )
    active = fields.Boolean(default=True, tracking=True)
    note = fields.Text(string='Internal Note', translate=True)

    @api.constrains('target_value')
    def _check_target_value(self):
        for rec in self:
            if rec.target_value < 0:
                raise ValidationError(_("KPI target value must be greater than or equal to 0."))
