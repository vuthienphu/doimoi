# -*- coding: utf-8 -*-
from odoo import fields, models


TRAINING_RESULT_SELECTION = [
    ('passed', 'Passed'),
    ('failed', 'Failed'),
    ('in_progress', 'In Progress'),
    ('cancelled', 'Cancelled'),
]


class DcgEmployeeTraining(models.Model):
    _name = 'dcg.employee.training'
    _description = 'Employee Training'
    _order = 'start_date desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', index=True,
    )
    course_name = fields.Char(string='Course', required=True)
    provider = fields.Char(string='Provider')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    hours = fields.Float(string='Hours')
    result = fields.Selection(
        selection=TRAINING_RESULT_SELECTION, string='Result',
    )
    has_certificate = fields.Boolean(string='Certificate Received')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_employee_training_attachment_rel',
        'training_id', 'attachment_id', string='Attachments',
    )
    note = fields.Text(string='Note')
