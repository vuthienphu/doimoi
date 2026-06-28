# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgResourceCapacity(models.Model):
    _name = 'dcg.resource.capacity'
    _description = 'Resource Capacity'
    _order = 'period_start desc, employee_id'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, index=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id', string='Department', store=True,
    )
    role_id = fields.Many2one('dcg.resource.role', string='Primary Role')
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

    # Hours
    capacity_hours = fields.Float(
        string='Capacity (h)', default=160,
        help='Total working hours in this period.',
    )
    allocated_hours = fields.Float(
        string='Allocated (h)', compute='_compute_hours', store=True,
    )
    actual_hours = fields.Float(
        string='Actual (h)', compute='_compute_hours', store=True,
    )
    available_hours = fields.Float(
        string='Available (h)', compute='_compute_hours', store=True,
    )
    billable_hours = fields.Float(
        string='Billable (h)', compute='_compute_hours', store=True,
    )

    # Rates
    allocation_rate = fields.Float(
        string='Allocation Rate (%)', compute='_compute_rates', store=True,
    )
    utilization_rate = fields.Float(
        string='Utilization Rate (%)', compute='_compute_rates', store=True,
    )
    bench_hours = fields.Float(
        string='Bench (h)', compute='_compute_rates', store=True,
    )

    _sql_constraints = [
        ('employee_period_uniq', 'UNIQUE(employee_id, period_start)',
         'Capacity snapshot already exists for this employee and period.'),
    ]

    @api.depends('period_start')
    def _compute_period_label(self):
        for rec in self:
            if rec.period_start:
                rec.period_label = rec.period_start.strftime('%Y-%m')
            else:
                rec.period_label = ''

    @api.depends('employee_id', 'period_start', 'period_end', 'capacity_hours')
    def _compute_hours(self):
        Alloc = self.env['dcg.resource.allocation']
        Line = self.env['account.analytic.line']
        for rec in self:
            if not (rec.employee_id and rec.period_start and rec.period_end):
                rec.allocated_hours = rec.actual_hours = rec.available_hours = rec.billable_hours = 0
                continue
            allocs = Alloc.search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', 'not in', ['cancelled']),
                ('start_date', '<=', rec.period_end),
                ('end_date', '>=', rec.period_start),
            ])
            # Pro-rate allocation hours to this period
            total_alloc = 0
            for a in allocs:
                overlap_start = max(a.start_date, rec.period_start)
                overlap_end = min(a.end_date, rec.period_end)
                overlap_days = (overlap_end - overlap_start).days + 1
                total_days = (a.end_date - a.start_date).days + 1
                if total_days > 0:
                    total_alloc += a.allocation_hours * overlap_days / total_days
            rec.allocated_hours = total_alloc
            rec.available_hours = max((rec.capacity_hours or 0) - total_alloc, 0)
            # Actual from timesheet
            lines = Line.search([
                ('employee_id', '=', rec.employee_id.id),
                ('line_state', '=', 'approved'),
                ('date', '>=', rec.period_start),
                ('date', '<=', rec.period_end),
            ])
            rec.actual_hours = sum(lines.mapped('unit_amount'))
            rec.billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type == 'billable'
            )

    @api.depends('capacity_hours', 'allocated_hours', 'billable_hours')
    def _compute_rates(self):
        for rec in self:
            cap = rec.capacity_hours or 1
            rec.allocation_rate = rec.allocated_hours / cap * 100
            rec.utilization_rate = rec.billable_hours / cap * 100
            rec.bench_hours = max(cap - rec.allocated_hours, 0)
