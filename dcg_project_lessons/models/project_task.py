# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    lesson_ids = fields.One2many('project.lesson', 'task_id', string='Bài học kinh nghiệm')
    lesson_count = fields.Integer(string='Số bài học', compute='_compute_lesson_count')

    def _compute_lesson_count(self):
        for task in self:
            task.lesson_count = len(task.lesson_ids)

    def action_open_task_lessons(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bài học kinh nghiệm',
            'res_model': 'project.lesson',
            'view_mode': 'list,form,kanban,pivot,graph',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_project_id': self.project_id.id,
                'default_task_id': self.id,
            },
        }
