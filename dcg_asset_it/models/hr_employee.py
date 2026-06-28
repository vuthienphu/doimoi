# -*- coding: utf-8 -*-
from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    assigned_asset_ids = fields.One2many(
        'dcg.asset.assignment', 'employee_id', string='Asset Assignments',
        domain=[('status', '=', 'assigned')],
    )
    assigned_asset_count = fields.Integer(compute='_compute_asset_count')

    def _compute_asset_count(self):
        Assignment = self.env['dcg.asset.assignment']
        for emp in self:
            emp.assigned_asset_count = Assignment.search_count([
                ('employee_id', '=', emp.id), ('status', '=', 'assigned'),
            ]) if emp.id else 0

    def action_view_assets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assigned Assets',
            'res_model': 'dcg.asset',
            'view_mode': 'list,form',
            'domain': [('current_employee_id', '=', self.id)],
        }
