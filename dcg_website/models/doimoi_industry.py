# -*- coding: utf-8 -*-

from odoo import fields, models


class DoimoiIndustry(models.Model):
    _name = 'doimoi.industry'
    _description = 'Ngành trọng tâm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Tên ngành', required=True, tracking=True)
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    icon = fields.Char(
        string='Biểu tượng ngành',
        required=True,
        default='🏭',
        help='Nhập một biểu tượng ngắn, ví dụ: ⚡, 🏭, ⛏️.',
        tracking=True,
    )
    cover_image = fields.Image(
        string='Ảnh đại diện',
        max_width=1600,
        max_height=900,
        help='Ảnh ngang tỷ lệ 16:9 hiển thị phía trên thẻ ngành.',
    )
    short_description = fields.Text(string='Mô tả ngắn', required=True, tracking=True)
    theme = fields.Selection(
        selection=[
            ('orange', 'Cam'),
            ('teal', 'Xanh ngọc'),
            ('purple', 'Tím'),
            ('rose', 'Hồng'),
            ('blue', 'Xanh dương'),
            ('green', 'Xanh lá'),
        ],
        string='Màu giao diện',
        required=True,
        default='orange',
        tracking=True,
    )
    feature_ids = fields.One2many(
        'doimoi.industry.feature',
        'industry_id',
        string='Năng lực nổi bật',
    )
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)


class DoimoiIndustryFeature(models.Model):
    _name = 'doimoi.industry.feature'
    _description = 'Năng lực theo ngành'
    _order = 'sequence, id'

    name = fields.Char(string='Năng lực', required=True)
    industry_id = fields.Many2one(
        'doimoi.industry',
        string='Ngành',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Thứ tự', default=10)
