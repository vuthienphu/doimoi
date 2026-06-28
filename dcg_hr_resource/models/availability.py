# -*- coding: utf-8 -*-
from odoo import fields, models


AVAILABILITY_STATUS_SELECTION = [
    ('available', 'Available'),
    ('partial', 'Partially Available'),
    ('allocated', 'Fully Allocated'),
    ('leave', 'On Leave'),
    ('training', 'Training'),
    ('resigned', 'Resigned'),
]


class DcgEmployeeAvailability(models.Model):
    _name = 'dcg.employee.availability'
    _description = 'Employee Availability'
    _order = 'available_from desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', index=True,
    )
    available_from = fields.Date(string='From', required=True)
    available_to = fields.Date(string='To', required=True)
    available_hours = fields.Float(string='Available Hours')
    status = fields.Selection(
        selection=AVAILABILITY_STATUS_SELECTION, string='Status',
        default='available', required=True,
    )
    note = fields.Text(string='Note')
