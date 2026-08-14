# -*- coding: utf-8 -*-

from odoo import models, fields

class DoimoiStatistic(models.Model):
    _name = 'doimoi.statistic'
    _description = 'Số liệu nổi bật'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    value = fields.Char(string='Giá trị', required=True, help="VD: 15+, 1000+, 24/7", tracking=True)
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    label = fields.Char(string='Nhãn mô tả', required=True, help="VD: Năm kinh nghiệm", tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)
