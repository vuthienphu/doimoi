from odoo import api, fields, models, _


class HelpdeskTicketCreateTaskWizard(models.TransientModel):
    _name = 'helpdesk.ticket.create.task.wizard'
    _description = 'Wizard tạo Task từ Yêu cầu hỗ trợ'

    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Phiếu hỗ trợ',
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Công ty',
        related='ticket_id.partner_id',
        readonly=True,
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Dự án',
        required=True,
        domain="[('partner_id', '=', partner_id)]",
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Người thực hiện',
    )
    task_name = fields.Char(
        string='Tên Task',
        required=True,
    )
    description = fields.Html(
        string='Nội dung mô tả',
    )
    date_deadline = fields.Date(
        string='Hạn chót',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ticket_id = self.env.context.get('default_ticket_id') or self.env.context.get('active_id')
        if ticket_id:
            ticket = self.env['helpdesk.ticket'].browse(ticket_id)
            if ticket.exists():
                res['ticket_id'] = ticket.id
                if 'project_id' in fields_list and ticket.project_id:
                    res['project_id'] = ticket.project_id.id
                if 'task_name' in fields_list:
                    res['task_name'] = ticket.name
                if 'description' in fields_list:
                    res['description'] = ticket.description
        return res

    def action_create_task(self):
        self.ensure_one()
        task_vals = {
            'name': self.task_name,
            'description': self.description,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'date_deadline': self.date_deadline,
            'helpdesk_ticket_id': self.ticket_id.id,
        }
        if self.user_ids:
            task_vals['user_ids'] = [fields.Command.set(self.user_ids.ids)]

        task = self.env['project.task'].create(task_vals)

        return {
            'name': _('Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': task.id,
            'view_mode': 'form',
        }
