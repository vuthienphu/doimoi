# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

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

    def _check_task_manager_edit_access(self):
        if (
            not self.env.context.get('dcg_task_creation')
            and not self.env.su
            and not self.env.user.has_group('project.group_project_manager')
        ):
            raise UserError(_(
                'Bạn cần có quyền Quản lý dự án để chỉnh sửa Danh sách kiểm tra.'
            ))

    @api.model_create_multi
    def create(self, vals_list):
        self._check_task_manager_edit_access()
        return super().create(vals_list)

    def write(self, vals):
        self._check_task_manager_edit_access()
        if vals.get('is_done'):
            unchecked = self.filtered(lambda checklist: not checklist.is_done)
            if unchecked:
                super(TaskChecklist, unchecked).write({
                    'finish_date': fields.Datetime.now(),
                    'reviewer_id': self.env.user.id,
                })
        return super().write(vals)

    def unlink(self):
        self._check_task_manager_edit_access()
        return super().unlink()
