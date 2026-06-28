# -*- coding: utf-8 -*-
from odoo import fields, models

ASSIGNMENT_STATUS = [
    ('assigned', 'Assigned'),
    ('returned', 'Returned'),
    ('lost', 'Lost'),
    ('broken', 'Broken'),
]

class DcgAssetAssignment(models.Model):
    _name = 'dcg.asset.assignment'
    _description = 'Asset Assignment'
    _order = 'assigned_date desc'

    asset_id = fields.Many2one('dcg.asset', string='Asset', required=True, ondelete='cascade', index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    project_id = fields.Many2one('dcg.project.delivery', string='Project')
    department_id = fields.Many2one('hr.department', string='Department')
    assigned_date = fields.Date(string='Assigned Date', required=True, default=fields.Date.context_today)
    returned_date = fields.Date(string='Returned Date')
    status = fields.Selection(selection=ASSIGNMENT_STATUS, string='Status', default='assigned', required=True)
    assigned_by_id = fields.Many2one('res.users', string='Assigned By', default=lambda self: self.env.user)
    note = fields.Text(string='Note')
