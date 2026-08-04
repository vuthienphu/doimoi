# -*- coding: utf-8 -*-

from odoo import fields, models

class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = 'Checklist của công việc'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nội dung kiểm tra', required=True)
    is_done = fields.Boolean(string='Đã hoàn thành')
    finish_date = fields.Datetime(string='Thời gian hoàn thành')
    reviewer_id = fields.Many2one('res.users', string='Người xác nhận')
    task_id = fields.Many2one(
        'project.task',
        string='Công việc',
        required=True,
        ondelete='cascade',
    )

    def write(self, vals):
        if vals.get('is_done'):
            unchecked = self.filtered(lambda checklist: not checklist.is_done)
            if unchecked:
                super(TaskChecklist, unchecked).write({
                    'finish_date': fields.Datetime.now(),
                    'reviewer_id': self.env.user.id,
                })
        return super().write(vals)
