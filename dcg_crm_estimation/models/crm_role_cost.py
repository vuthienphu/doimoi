# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmRoleCost(models.Model):
    _name = 'crm.role.cost'
    _description = 'Đơn giá nhân sự CRM'
    _rec_name = 'role'
    _order = 'role'

    role = fields.Selection(
        [
            ('ba', 'BA'),
            ('backend', 'Backend'),
            ('frontend', 'Frontend'),
            ('qa', 'QA'),
            ('devops', 'DevOps'),
            ('uiux', 'UI/UX'),
        ],
        string='Vai trò',
        required=True,
    )
    cost_per_md = fields.Monetary(string='Đơn giá / MD', required=True, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    active = fields.Boolean(string='Có hiệu lực', default=True)

    _sql_constraints = [
        ('uniq_active_role', 'unique(role, active)', 'Mỗi vai trò chỉ được có một đơn giá có hiệu lực tại một thời điểm!'),
    ]
