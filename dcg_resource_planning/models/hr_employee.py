# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    primary_role_id = fields.Many2one(
        'dcg.resource.role', string='Primary Role',
    )
    skill_ids = fields.One2many(
        'dcg.resource.skill', 'employee_id', string='Skills',
    )
    allocation_ids = fields.One2many(
        'dcg.resource.allocation', 'employee_id', string='Allocations',
    )
    capacity_ids = fields.One2many(
        'dcg.resource.capacity', 'employee_id', string='Capacity History',
    )

    current_allocation_percent = fields.Float(
        string='Current Alloc (%)', compute='_compute_current_allocation',
    )
    is_on_bench = fields.Boolean(
        string='On Bench', compute='_compute_current_allocation',
    )
    skill_count = fields.Integer(compute='_compute_counts')
    active_allocation_count = fields.Integer(compute='_compute_counts')

    def _compute_current_allocation(self):
        today = fields.Date.today()
        Alloc = self.env['dcg.resource.allocation']
        for emp in self:
            active_allocs = Alloc.search([
                ('employee_id', '=', emp.id),
                ('state', 'not in', ['cancelled', 'done']),
                ('start_date', '<=', today),
                ('end_date', '>=', today),
            ])
            emp.current_allocation_percent = sum(active_allocs.mapped('allocation_percent'))
            emp.is_on_bench = emp.current_allocation_percent < 10

    def _compute_counts(self):
        today = fields.Date.today()
        Alloc = self.env['dcg.resource.allocation']
        for emp in self:
            emp.skill_count = len(emp.skill_ids)
            emp.active_allocation_count = Alloc.search_count([
                ('employee_id', '=', emp.id),
                ('state', 'not in', ['cancelled', 'done']),
                ('start_date', '<=', today),
                ('end_date', '>=', today),
            ])
