from odoo import models, fields


class SolutionModuleSurveyChecklist(models.Model):
    _name = 'solution.module.survey.checklist'
    _description = 'Checklist Khảo sát'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Nội dung khảo sát', required=True)
    description = fields.Text(string='Mô tả mục đích')
    required = fields.Boolean(string='Bắt buộc', default=False)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
