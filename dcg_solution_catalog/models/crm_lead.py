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
                    project.write({'solution_ids': [(6, 0, lead.solution_ids.ids)]})

                existing_task_names = set(project.task_ids.mapped('name'))
                tasks_to_create = []

                for solution in lead.solution_ids:
                    for tmpl in solution.task_template_ids:
                        if tmpl.name not in existing_task_names:
                            tasks_to_create.append({
                                'name': tmpl.name,
                                'description': tmpl.description,
                                'allocated_hours': tmpl.planned_hours,
                                'project_id': project.id,
                                'partner_id': lead.partner_id.id if lead.partner_id else False,
                                'solution_ids': [(6, 0, [solution.id])],
                            })
                            existing_task_names.add(tmpl.name)

                if tasks_to_create:
                    self.env['project.task'].create(tasks_to_create)
