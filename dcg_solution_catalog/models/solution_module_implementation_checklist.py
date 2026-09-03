from odoo import models, fields


class SolutionModuleImplementationChecklist(models.Model):
    _name = 'solution.module.implementation.checklist'
    _description = 'Checklist Triển khai'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Công việc triển khai', required=True)
    description = fields.Text(string='Mô tả chi tiết')
    required = fields.Boolean(string='Bắt buộc', default=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
