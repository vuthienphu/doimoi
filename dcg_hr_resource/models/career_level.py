# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgEmployeeCareerLevel(models.Model):
    _name = 'dcg.employee.career.level'
    _description = 'Employee Career Level'
    _order = 'sequence'

    name = fields.Char(string='Level', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)
    minimum_years = fields.Float(string='Min Experience (years)')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
