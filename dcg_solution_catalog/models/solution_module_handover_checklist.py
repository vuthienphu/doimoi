from odoo import models, fields


class SolutionModuleHandoverChecklist(models.Model):
    _name = 'solution.module.handover.checklist'
    _description = 'Checklist Bàn giao'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Điều kiện bàn giao / Nghiệm thu', required=True)
    description = fields.Text(string='Mô tả tiêu chuẩn')
    required = fields.Boolean(string='Bắt buộc', default=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
