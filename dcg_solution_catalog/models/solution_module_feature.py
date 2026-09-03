from odoo import models, fields


class SolutionModuleFeature(models.Model):
    _name = 'solution.module.feature'
    _description = 'Chức năng Giải pháp'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Tên chức năng', required=True)
    description = fields.Text(string='Mô tả')
    image = fields.Binary(string='Hình ảnh minh họa')
    note = fields.Char(string='Ghi chú (Standard/Custom)')
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
