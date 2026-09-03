from odoo import models, fields, api, _


class ProjectSolutionChangeWarningWizard(models.TransientModel):
    _name = 'project.solution.change.warning.wizard'
    _description = 'Wizard Cảnh Báo Loại Bỏ Giải Pháp Trên Dự Án'

    project_id = fields.Many2one('project.project', string='Dự án', required=True, readonly=True)
    removed_solution_ids = fields.Many2many('solution.module', string='Giải pháp bị loại bỏ', readonly=True)
    new_solution_ids = fields.Many2many('solution.module', 'wizard_new_solution_rel', string='Danh sách giải pháp mới', readonly=True)
    affected_task_ids = fields.Many2many('project.task', string='Task bị ảnh hưởng', readonly=True)
    message = fields.Html(string='Nội dung cảnh báo', readonly=True)

    def action_continue(self):
        self.ensure_one()
        # Save new solutions onto project without triggering warning again
        self.project_id.with_context(skip_solution_check=True).write({
            'solution_ids': [(6, 0, self.new_solution_ids.ids)]
        })
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
