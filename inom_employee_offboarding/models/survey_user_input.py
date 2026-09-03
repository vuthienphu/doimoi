# -*- coding: utf-8 -*-
from odoo import fields, models


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    manager_offboard_id = fields.Many2one(
        'hr.employee',
        string='Quản lý offboard',
        help='Quản lý trực tiếp của nhân viên tại thời điểm tạo khảo sát nghỉ việc.',
    )
