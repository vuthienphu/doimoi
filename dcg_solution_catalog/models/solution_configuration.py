from odoo import models, fields


class SolutionConfiguration(models.Model):
    _name = 'solution.configuration'
    _description = 'Cấu hình phân hệ'
    _order = 'sequence, name'

    name = fields.Char(string='Tên phân hệ', required=True)
    code = fields.Char(string='Mã phân hệ')
    description = fields.Text(string='Mô tả')
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
