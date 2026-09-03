from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    solution_ids = fields.Many2many(
        comodel_name='solution.module',
        relation='project_project_solution_module_rel',
        column1='project_id',
        column2='solution_id',
        string='Giải pháp',
        domain="[('state', '=', 'ready')]",
    )

    def write(self, vals):
        if 'solution_ids' in vals and not self.env.context.get('skip_solution_check'):
            for project in self:
                old_solution_ids = project.solution_ids.ids
                new_commands = vals['solution_ids']
                new_solution_ids = project._eval_solution_ids_commands(old_solution_ids, new_commands)

                removed_ids = set(old_solution_ids) - set(new_solution_ids)
                if removed_ids:
                    affected_tasks = self.env['project.task'].search([
                        ('project_id', '=', project.id),
                        ('solution_ids', 'in', list(removed_ids)),
                    ])
                    if affected_tasks:
                        wizard = self.env['project.solution.change.warning.wizard'].create({
                            'project_id': project.id,
                            'removed_solution_ids': [(6, 0, list(removed_ids))],
                            'new_solution_ids': [(6, 0, new_solution_ids)],
                            'affected_task_ids': [(6, 0, affected_tasks.ids)],
                        })
                        return {
                            'name': _('Cảnh Báo Thay Đổi Giải Pháp Dự Án'),
                            'type': 'ir.actions.act_window',
                            'res_model': 'project.solution.change.warning.wizard',
                            'res_id': wizard.id,
                            'view_mode': 'form',
                            'target': 'new',
                        }

        return super().write(vals)

    def _eval_solution_ids_commands(self, current_ids, commands):
        result_set = set(current_ids)
        for cmd in commands:
            if isinstance(cmd, (list, tuple)):
                op = cmd[0]
                if op == 6:
                    result_set = set(cmd[2])
                elif op == 4:
                    result_set.add(cmd[1])
                elif op == 3:
                    result_set.discard(cmd[1])
                elif op == 5:
                    result_set.clear()
        return list(result_set)
