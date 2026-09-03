# -*- coding: utf-8 -*-
from odoo import fields, models


class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    min_notice_days = fields.Integer('Số ngày tối thiểu phải báo trước khi chấm dứt HĐLĐ')
