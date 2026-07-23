from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    lesson_ids = fields.One2many('project.lesson', 'task_id', string='Bài học kinh nghiệm')
    caution_lesson_ids = fields.Many2many(
        'project.lesson',
        'project_task_project_lesson_caution_rel',
        'task_id',
        'lesson_id',
        string='Bài học cần lưu ý',
    )
    lesson_count = fields.Integer(string='Số bài học', compute='_compute_lesson_count')
    estimated_md = fields.Float(string='MD Ước tính', default=0.0, tracking=True)
    actual_md = fields.Float(
        string='MD Thực tế',
        compute='_compute_actual_md',
        store=True,
    )
    variance_md = fields.Float(
        string='Chênh lệch (Variance)',
        compute='_compute_variance_md',
        store=True,
    )

    @api.depends('timesheet_ids.unit_amount')
    def _compute_actual_md(self):
        for task in self:
            if hasattr(task, 'timesheet_ids'):
                task.actual_md = sum(task.timesheet_ids.mapped('unit_amount')) / 8.0
            else:
                task.actual_md = 0.0

    @api.depends('estimated_md', 'actual_md')
    def _compute_variance_md(self):
        for task in self:
            task.variance_md = task.actual_md - task.estimated_md

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
