# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmPaymentType(models.Model):
    _name = 'crm.payment.type'
    _description = 'Loại thanh toán CRM'
    _order = 'name'

    name = fields.Char(string='Tên loại thanh toán', required=True)
    cycle_days = fields.Integer(string='Chu kỳ thanh toán (ngày)', default=30, required=True)
    remind_before_days = fields.Integer(string='Số ngày nhắc trước kỳ', default=5, required=True)
    active = fields.Boolean(string='Có hiệu lực', default=True)
