# -*- coding: utf-8 -*-

from odoo import models, fields

class CrmExchangeHistory(models.Model):
    _name = 'crm.exchange.history'
    _description = 'Lịch sử trao đổi'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', ondelete='cascade')
    
    user_id = fields.Many2one('res.users', string='Người trao đổi', default=lambda self: self.env.user)
    date = fields.Datetime(string='Ngày trao đổi', default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Trao đổi với ai')
    exchange_method = fields.Selection([
        ('email', 'Email'),
        ('call', 'Gọi điện'),
        ('offline', 'Offline'),
        ('other', 'Khác')
    ], string='Phương tiện trao đổi')
    content = fields.Html(string='Nội dung trao đổi')
    attachment_ids = fields.Many2many('ir.attachment', string='Đính kèm')
