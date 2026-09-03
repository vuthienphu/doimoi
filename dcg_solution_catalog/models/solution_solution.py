from odoo import models, fields


class SolutionSolution(models.Model):
    _name = 'solution.solution'
    _description = 'Danh mục Giải pháp'
    _order = 'sequence, name'

    name = fields.Char(string='Tên giải pháp', required=True)
    code = fields.Char(string='Mã giải pháp')
    description = fields.Text(string='Mô tả')
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
