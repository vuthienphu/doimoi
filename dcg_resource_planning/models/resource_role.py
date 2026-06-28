# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgResourceRole(models.Model):
    _name = 'dcg.resource.role'
    _description = 'Resource Role'
    _order = 'sequence, name'

    name = fields.Char(string='Role', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    department_id = fields.Many2one('hr.department', string='Department')
    default_cost_rate = fields.Float(
        string='Default Cost Rate',
        help='Default internal cost rate per hour.',
    )
    default_bill_rate = fields.Float(
        string='Default Bill Rate',
        help='Default billing rate per hour.',
    )
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color')

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Role code must be unique.'),
    ]
