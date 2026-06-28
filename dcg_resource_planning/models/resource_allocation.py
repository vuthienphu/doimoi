# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


ALLOC_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
]

RESOURCE_TYPE_SELECTION = [
    ('employee', 'Employee'),
    ('freelancer', 'Freelancer'),
    ('vendor', 'Vendor'),
    ('intern', 'Intern'),
]


class DcgResourceAllocation(models.Model):
    _name = 'dcg.resource.allocation'
    _description = 'Resource Allocation'
    _order = 'start_date, employee_id'

    plan_id = fields.Many2one(
        'dcg.resource.plan', string='Resource Plan',
        ondelete='cascade', index=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True, index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, index=True,
    )
    user_id = fields.Many2one(
        related='employee_id.user_id', string='User', store=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id', string='Department', store=True,
    )
    role_id = fields.Many2one(
        'dcg.resource.role', string='Role', required=True,
    )
    resource_type = fields.Selection(
        selection=RESOURCE_TYPE_SELECTION, string='Resource Type',
        default='employee',
    )
    state = fields.Selection(
        selection=ALLOC_STATE_SELECTION, string='Status',
        default='draft',
    )

    # Period
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    # Allocation
    allocation_percent = fields.Float(
        string='Allocation (%)', default=100.0,
        help='Percentage of working time allocated to this project.',
    )
    allocation_hours = fields.Float(
        string='Allocated Hours',
        compute='_compute_allocation_hours', store=True, readonly=False,
    )
    actual_hours = fields.Float(
        string='Actual Hours', compute='_compute_actual_hours', store=True,
    )
    variance_hours = fields.Float(
        string='Variance', compute='_compute_actual_hours', store=True,
    )

    # Cost
    cost_rate = fields.Float(string='Cost Rate (h)')
    bill_rate = fields.Float(string='Bill Rate (h)')
    is_billable = fields.Boolean(string='Billable', default=True)

    note = fields.Text(string='Note')

    # Over-allocation check
    total_allocation_percent = fields.Float(
        string='Total Alloc (%)', compute='_compute_total_allocation',
        help='Total allocation of this employee across all projects in this period.',
    )
    is_over_allocated = fields.Boolean(
        string='Over-allocated', compute='_compute_total_allocation', stored=True
    )

    @api.depends('allocation_percent', 'start_date', 'end_date')
    def _compute_allocation_hours(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date >= rec.start_date:
                delta = (rec.end_date - rec.start_date).days + 1
                work_days = delta * 5 / 7  # rough estimate
                rec.allocation_hours = work_days * 8 * (rec.allocation_percent or 0) / 100
            else:
                rec.allocation_hours = 0

    @api.depends('project_id', 'employee_id', 'start_date', 'end_date')
    def _compute_actual_hours(self):
        Line = self.env['account.analytic.line']
        for rec in self:
            if rec.project_id and rec.employee_id and rec.start_date and rec.end_date:
                lines = Line.search([
                    ('dcg_project_id', '=', rec.project_id.id),
                    ('employee_id', '=', rec.employee_id.id),
                    ('line_state', '=', 'approved'),
                    ('date', '>=', rec.start_date),
                    ('date', '<=', rec.end_date),
                ])
                rec.actual_hours = sum(lines.mapped('unit_amount'))
            else:
                rec.actual_hours = 0
            rec.variance_hours = rec.actual_hours - (rec.allocation_hours or 0)

    @api.depends('employee_id', 'start_date', 'end_date', 'allocation_percent')
    def _compute_total_allocation(self):
        for rec in self:
            if rec.employee_id and rec.start_date and rec.end_date:
                overlapping = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', 'not in', ['cancelled']),
                    ('start_date', '<=', rec.end_date),
                    ('end_date', '>=', rec.start_date),
                ])
                rec.total_allocation_percent = sum(overlapping.mapped('allocation_percent'))
                rec.is_over_allocated = rec.total_allocation_percent > 100
            else:
                rec.total_allocation_percent = 0
                rec.is_over_allocated = False

    @api.onchange('role_id')
    def _onchange_role_id(self):
        if self.role_id:
            self.cost_rate = self.role_id.default_cost_rate
            self.bill_rate = self.role_id.default_bill_rate

    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        if self.plan_id:
            self.project_id = self.plan_id.project_id

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
