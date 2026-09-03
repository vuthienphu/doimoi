# -*- coding: utf-8 -*-
from odoo import fields, models


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    is_exit_interview = fields.Boolean(
        string='Là khảo sát nghỉ việc',
        default=False,
        help='Khi bật, nhân viên không được làm lại hay sửa kết quả sau khi '
             'đã hoàn thành khảo sát.',
    )
