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

    source_module_id = fields.Many2one(
        'solution.module',
        string='Module nguồn',
        readonly=True,
        copy=False,
        index=True,
        help='Module giải pháp mà Task này được tự động sinh ra. '
             'Rỗng nếu Task được tạo thủ công.',
    )
    source_task_template_id = fields.Many2one(
        'solution.module.task.template',
        string='Mẫu công việc nguồn',
        readonly=True,
        copy=False,
        index=True,
        ondelete='set null',
        help='Mẫu công việc (Task Template) mà Task này được tự động sinh ra. '
             'Dùng để chống sinh trùng Task khi đồng bộ lại giải pháp.',
    )
    source_lead_id = fields.Many2one(
        'crm.lead',
        string='Cơ hội nguồn',
        readonly=True,
        copy=False,
        index=True,
        help='Cơ hội CRM đã tạo ra Dự án (và do đó gián tiếp tạo ra Task này), '
             'nếu Dự án được tạo tự động từ CRM.',
    )
    is_auto_generated = fields.Boolean(
        string='Task tự động sinh',
        compute='_compute_is_auto_generated',
        store=True,
        help='True nếu Task được hệ thống tự sinh từ Mẫu công việc của giải pháp.',
    )

    @api.depends('source_task_template_id')
    def _compute_is_auto_generated(self):
        for task in self:
            task.is_auto_generated = bool(task.source_task_template_id)

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