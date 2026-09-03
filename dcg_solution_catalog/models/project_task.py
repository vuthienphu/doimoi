from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    solution_ids = fields.Many2many(
        comodel_name='solution.module',
        relation='project_task_solution_module_rel',
        column1='task_id',
        column2='solution_id',
        string='Giải pháp',
    )

    @api.onchange('project_id')
    def _onchange_project_id_solution(self):
        if self.project_id and self.project_id.solution_ids:
            self.solution_ids = [(6, 0, self.project_id.solution_ids.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'project_id' in vals and 'solution_ids' not in vals:
                project = self.env['project.project'].browse(vals['project_id'])
                if project.exists() and project.solution_ids:
                    vals['solution_ids'] = [(6, 0, project.solution_ids.ids)]
        return super().create(vals_list)
