# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    lesson_ids = fields.One2many('project.lesson', 'project_id', string='Bài học kinh nghiệm')
    lesson_count = fields.Integer(string='Số bài học', compute='_compute_lesson_count')

    def _compute_lesson_count(self):
        for project in self:
            project.lesson_count = len(project.lesson_ids)

    def action_open_project_lessons(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bài học kinh nghiệm',
            'res_model': 'project.lesson',
            'view_mode': 'list,form,kanban,pivot,graph',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }

    def action_archive(self):
        projects_with_draft_lessons = self.filtered(
            lambda project: project.active and project.lesson_ids.filtered(lambda lesson: lesson.state == 'draft')
        )
        if projects_with_draft_lessons and not self.env.context.get('skip_lesson_archive_warning'):
            wizard = self.env['project.lesson.archive.warning'].create({
                'project_ids': [(6, 0, projects_with_draft_lessons.ids)],
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Bài học kinh nghiệm chưa xác nhận',
                'res_model': 'project.lesson.archive.warning',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
            }
        return super().action_archive()
