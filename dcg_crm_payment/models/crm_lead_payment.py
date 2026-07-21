# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmLeadPayment(models.Model):
    _name = 'crm.lead.payment'
    _description = 'Chi tiết thanh toán cơ hội'
    _order = 'payment_date desc, due_date desc'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, ondelete='cascade')
    payment_date = fields.Date(string='Thời gian thanh toán', required=True)
    expected_amount = fields.Monetary(string='Giá trị phải thanh toán', required=True, currency_field='currency_id')
    paid_amount = fields.Monetary(string='Giá trị thanh toán', required=True, currency_field='currency_id')
    due_date = fields.Date(string='Ngày đến hạn', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='lead_id.currency_id',
        store=True,
        readonly=True,
    )
