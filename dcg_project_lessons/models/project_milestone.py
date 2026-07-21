# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    lesson_ids = fields.One2many('project.lesson', 'milestone_id', string='Bài học kinh nghiệm')
    lesson_count = fields.Integer(string='Số bài học', compute='_compute_lesson_count')

    def _compute_lesson_count(self):
        for milestone in self:
            milestone.lesson_count = len(milestone.lesson_ids)

    def action_open_milestone_lessons(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bài học kinh nghiệm',
            'res_model': 'project.lesson',
            'view_mode': 'list,form,kanban,pivot,graph',
            'domain': [('milestone_id', '=', self.id)],
            'context': {
                'default_project_id': self.project_id.id,
                'default_milestone_id': self.id,
            },
        }
