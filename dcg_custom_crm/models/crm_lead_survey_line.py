# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmLeadSurveyLine(models.Model):
    _name = 'crm.lead.survey.line'
    _description = 'Chi tiết đầu mục khảo sát Cơ hội'
    _order = 'sequence, id'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Thứ tự', default=10)
    module = fields.Char(string='Phân hệ/Module', required=True)
    name = fields.Char(string='Chức năng', required=True)
    current_state = fields.Text(string='Hiện trạng')
    desired_state = fields.Text(string='Mong muốn')
    priority = fields.Selection(
        [
            ('low', 'Thấp'),
            ('medium', 'Trung bình'),
            ('high', 'Cao'),
        ],
        string='Ưu tiên',
        default='medium',
        required=True,
    )
    is_standard = fields.Boolean(string='Chuẩn Odoo', default=True)
    solution = fields.Text(string='Giải pháp')
    notes = fields.Text(string='Ghi chú')
