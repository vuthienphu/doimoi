# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dcg_project_mail_from = fields.Char(
        string='Email gửi thông báo',
        config_parameter='dcg_project_customize.mail_from',
        help='Email dùng làm người gửi cho các thông báo Task của DCG Project Customize.',
    )
    dcg_project_mail_from_name = fields.Char(
        string='Tên người gửi',
        config_parameter='dcg_project_customize.mail_from_name',
        help='Tên hiển thị trong email gửi ra từ module DCG Project Customize.',
    )
