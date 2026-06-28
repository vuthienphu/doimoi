# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgCostCenter(models.Model):
    _name = 'dcg.cost.center'
    _description = 'Cost Center'
    _order = 'sequence, code, name'

    name = fields.Char(
        string='Cost Center',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        index=True,
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Internal Note', translate=True)

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Cost Center code must be unique.',
        ),
    ]
