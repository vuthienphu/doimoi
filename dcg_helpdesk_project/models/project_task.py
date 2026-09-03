from odoo import api, fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    helpdesk_ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Phiếu hỗ trợ',
        ondelete='set null',
        index=True,
    )

    def write(self, vals):
        res = super().write(vals)
        if 'stage_id' in vals or 'state' in vals or 'active' in vals:
            self._check_ticket_completion()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        tasks._check_ticket_completion()
        return tasks

    def _check_ticket_completion(self):
        tickets = self.mapped('helpdesk_ticket_id').filtered(lambda t: t.exists())
        for ticket in tickets:
            if not ticket.task_ids:
                continue
            all_done = True
            for task in ticket.task_ids:
                is_task_done = False
                if hasattr(task, 'state') and task.state in ('1_done', 'done', 'closed'):
                    is_task_done = True
                elif task.stage_id and task.stage_id.fold:
                    is_task_done = True

                if not is_task_done:
                    all_done = False
                    break

            if all_done:
                domain = [('fold', '=', True)]
                if ticket.team_id:
                    domain = [('team_ids', 'in', ticket.team_id.id)] + domain

                done_stage = self.env['helpdesk.stage'].search(domain, limit=1)
                if not done_stage and ticket.team_id:
                    done_stage = self.env['helpdesk.stage'].search([('fold', '=', True)], limit=1)

                if done_stage and ticket.stage_id != done_stage:
                    ticket.sudo().write({'stage_id': done_stage.id})
