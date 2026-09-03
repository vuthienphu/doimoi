from odoo import fields, models


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _description = 'Trạng thái Yêu cầu'
    _order = 'sequence, id'

    name = fields.Char(string='Tên trạng thái', required=True, translate=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    fold = fields.Boolean(string='Gấp/Hoàn tất trong Kanban')
    active = fields.Boolean(string='Kích hoạt', default=True)
    team_ids = fields.Many2many('helpdesk.team', string='Đội ngũ áp dụng')
