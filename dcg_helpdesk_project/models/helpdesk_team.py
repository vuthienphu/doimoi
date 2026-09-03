from odoo import fields, models


class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _description = 'Đội ngũ Hỗ trợ'
    _order = 'sequence, id'

    name = fields.Char(string='Tên đội ngũ', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
