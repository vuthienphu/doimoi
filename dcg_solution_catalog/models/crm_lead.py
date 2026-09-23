from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    solution_ids = fields.Many2many(
        comodel_name='solution.module',
        relation='crm_lead_solution_module_rel',
        column1='lead_id',
        column2='solution_id',
        string='Giải pháp triển khai',
        domain="[('state', '=', 'ready')]",
    )

    total_solution_planned_hours = fields.Float(
        string='Tổng thời gian ước tính (giờ)',
        compute='_compute_total_solution_planned_hours',
        store=True,
    )

    @api.depends('solution_ids.task_template_ids.planned_hours')
    def _compute_total_solution_planned_hours(self):
        for lead in self:
            total = sum(lead.solution_ids.mapped('task_template_ids.planned_hours'))
            lead.total_solution_planned_hours = total

    def _dcg_create_project_for_won_opportunities(self):
        super()._dcg_create_project_for_won_opportunities()

        for lead in self:
            project = lead.project_id
            if project and lead.solution_ids:
                if not project.solution_ids:
                    # skip_solution_check: đây là lần gắn giải pháp đầu tiên khi Project
                    # vừa được tạo từ CRM, không cần cảnh báo loại bỏ giải pháp.
                    project.with_context(skip_solution_check=True).write({
                        'solution_ids': [(6, 0, lead.solution_ids.ids)],
                    })

                # Sinh Task từ toàn bộ Mẫu công việc của các Module đã gắn.
                # Method dùng chung này tự chống trùng theo Mẫu công việc (source_task_template_id)
                # và gán liên kết Module/Mẫu công việc/Cơ hội nguồn lên từng Task được tạo.
                project._dcg_generate_tasks_from_solutions(lead.solution_ids)