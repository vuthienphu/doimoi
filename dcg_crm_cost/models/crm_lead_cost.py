# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmLeadCost(models.Model):
    _name = 'crm.lead.cost'
    _description = 'Chi phí cơ hội'
    _order = 'date desc, id desc'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, ondelete='cascade')
    cost_type = fields.Selection(
        [
            ('license', 'Bản quyền (License)'),
            ('infra', 'Hạ tầng (Infra)'),
            ('partner', 'Đối tác (Partner)'),
            ('travel', 'Công tác (Travel)'),
            ('equipment', 'Thiết bị (Equipment)'),
            ('other', 'Khác (Other)'),
        ],
        string='Loại chi phí',
        default='other',
        required=True,
    )
    name = fields.Char(string='Tên chi phí', required=True)
    date = fields.Date(string='Ngày', default=fields.Date.context_today, required=True)
    amount = fields.Monetary(string='Số tiền', required=True, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='lead_id.currency_id',
        store=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Người ghi nhận',
        default=lambda self: self.env.user,
        required=True,
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'crm_lead_cost_attachment_rel',
        'cost_id',
        'attachment_id',
        string='Đính kèm',
    )
