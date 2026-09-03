from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Yêu cầu Hỗ trợ / Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Tiêu đề Yêu cầu', required=True, tracking=True)
    description = fields.Html(string='Nội dung mô tả')
    partner_id = fields.Many2one('res.partner', string='Khách hàng', tracking=True)
    stage_id = fields.Many2one('helpdesk.stage', string='Trạng thái', tracking=True, group_expand='_read_group_stage_ids')
    team_id = fields.Many2one('helpdesk.team', string='Đội ngũ hỗ trợ', tracking=True)
    user_id = fields.Many2one('res.users', string='Người phụ trách', tracking=True)
    priority = fields.Selection([
        ('0', 'Bình thường'),
        ('1', 'Ưu tiên'),
        ('2', 'Cao'),
        ('3', 'Khẩn cấp'),
    ], string='Độ ưu tiên', default='0')
    active = fields.Boolean(string='Kích hoạt', default=True)

    request_source = fields.Selection([
        ('web', 'Website'),
        ('zalo', 'Zalo'),
        ('internal', 'Nội bộ'),
        ('other', 'Khác'),
    ], string='Nguồn yêu cầu', default='internal', required=True)

    company_name = fields.Char(
        string='Tên công ty (Form)',
        help='Tên công ty do khách hàng điền từ form yêu cầu công khai',
    )
    contact_name = fields.Char(string='Họ và tên')
    contact_email = fields.Char(string='Email')
    contact_phone = fields.Char(string='Số điện thoại')
    contact_department = fields.Char(string='Phòng ban')
    contact_position = fields.Char(string='Chức vụ')

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Dự án',
        domain="[('partner_id', '=', partner_id)]",
        help='Dự án liên quan đến yêu cầu này. Được lọc theo Công ty chọn ở trường Khách hàng.',
    )

    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='helpdesk_ticket_id',
        string='Danh sách Task',
    )
    task_count = fields.Integer(
        string='Số lượng Task',
        compute='_compute_task_count',
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['helpdesk.stage'].search([])

    @api.depends('task_ids')
    def _compute_task_count(self):
        for ticket in self:
            ticket.task_count = len(ticket.task_ids)

    def action_open_ticket_tasks(self):
        self.ensure_one()
        return {
            'name': _('Danh sách Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.task_ids.ids)],
            'context': {
                'default_helpdesk_ticket_id': self.id,
                'default_project_id': self.project_id.id if self.project_id else False,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
            },
        }

    def action_create_task_wizard(self):
        self.ensure_one()
        if not self.partner_id or not self.project_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('Phải xác định Công ty và Dự án trước khi tạo Task.'),
                },
            }
        return {
            'name': _('Tạo Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket.create.task.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id,
                'default_project_id': self.project_id.id,
                'default_task_name': self.name,
                'default_description': self.description,
            },
        }
