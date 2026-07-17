# -*- coding: utf-8 -*-

from odoo import fields, models


class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = 'Checklist của công việc'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nội dung kiểm tra', required=True)
    is_done = fields.Boolean(string='Đã hoàn thành')
    task_id = fields.Many2one(
        'project.task',
        string='Công việc',
        required=True,
        ondelete='cascade',
    )
