from odoo import models, fields


class SolutionModuleTaskTemplate(models.Model):
    _name = 'solution.module.task.template'
    _description = 'Mẫu công việc triển khai'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Tên công việc mẫu', required=True)
    description = fields.Text(string='Mô tả công việc')
    planned_hours = fields.Float(string='Thời gian ước tính (giờ)', default=1.0)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
