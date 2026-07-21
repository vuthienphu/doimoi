# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.tools.translate import _


class ProjectLessonArchiveWarning(models.TransientModel):
    _name = 'project.lesson.archive.warning'
    _description = 'Cảnh báo lưu trữ dự án còn bài học chưa xác nhận'

    project_ids = fields.Many2many('project.project', string='Dự án', required=True)
    draft_lesson_count = fields.Integer(string='Số bài học nháp', compute='_compute_draft_lesson_count')

    def _compute_draft_lesson_count(self):
        for wizard in self:
            wizard.draft_lesson_count = self.env['project.lesson'].search_count([
                ('project_id', 'in', wizard.project_ids.ids),
                ('state', '=', 'draft'),
            ])

    def action_continue_archive(self):
        self.ensure_one()
        self.project_ids.with_context(skip_lesson_archive_warning=True).action_archive()
        return {'type': 'ir.actions.act_window_close'}

    def action_open_draft_lessons(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bài học kinh nghiệm đang ở trạng thái Nháp'),
            'res_model': 'project.lesson',
            'view_mode': 'list,form,kanban,pivot,graph',
            'domain': [
                ('project_id', 'in', self.project_ids.ids),
                ('state', '=', 'draft'),
            ],
            'context': {
                'default_project_id': self.project_ids[:1].id,
                'search_default_draft': 1,
            },
        }
