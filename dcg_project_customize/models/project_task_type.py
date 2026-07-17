# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_processing = fields.Boolean(string='Đang thực hiện')
    is_test = fields.Boolean(string='Chờ kiểm tra')
    is_done = fields.Boolean(string='Hoàn thành')
    is_live = fields.Boolean(string='Đã đưa lên Live')
    is_dcg_default = fields.Boolean(string='Giai đoạn mặc định DCG')
