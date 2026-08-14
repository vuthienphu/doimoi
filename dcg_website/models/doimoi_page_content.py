# -*- coding: utf-8 -*-

from odoo import fields, models


class DoimoiPageSection(models.Model):
    _name = 'doimoi.page.section'
    _description = 'Nội dung section website'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'page, sequence, id'

    name = fields.Char(string='Tên nội bộ', required=True, tracking=True)
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    page = fields.Selection([
        ('home', 'Trang chủ'),
        ('about', 'Về Đổi Mới'),
        ('contact', 'Liên hệ'),
        ('solutions', 'Giải pháp'),
        ('industries', 'Ngành'),
    ], string='Trang', required=True, tracking=True)
    key = fields.Char(string='Mã section', required=True, tracking=True)
    eyebrow = fields.Char(string='Nhãn nhỏ', tracking=True)
    title = fields.Char(string='Tiêu đề', tracking=True)
    subtitle = fields.Text(string='Mô tả ngắn', tracking=True)
    body = fields.Html(string='Nội dung', sanitize=True, tracking=True)
    secondary_body = fields.Html(string='Nội dung bổ sung', sanitize=True, tracking=True)
    button_label = fields.Char(string='Nhãn nút', tracking=True)
    button_url = fields.Char(string='Liên kết nút', tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)
    item_ids = fields.One2many('doimoi.page.item', 'section_id', string='Danh sách nội dung')


class DoimoiPageItem(models.Model):
    _name = 'doimoi.page.item'
    _description = 'Mục nội dung trong section'
    _order = 'sequence, id'

    section_id = fields.Many2one('doimoi.page.section', required=True, ondelete='cascade')
    icon = fields.Char(string='Icon / Chữ viết tắt')
    title = fields.Char(string='Tiêu đề', required=True)
    subtitle = fields.Text(string='Mô tả')
    meta = fields.Char(string='Thông tin phụ')
    item_group = fields.Selection([
        ('benefit', 'Lợi ích / Điểm nổi bật'),
        ('process', 'Quy trình / Các bước'),
    ], string='Nhóm hiển thị', default='benefit', required=True)
    image = fields.Image(string='Ảnh', max_width=800, max_height=800)
    theme = fields.Selection([
        ('orange', 'Cam'), ('teal', 'Xanh ngọc'), ('blue', 'Xanh dương'),
        ('purple', 'Tím'), ('gray', 'Xám'),
    ], string='Màu', default='orange')
    sequence = fields.Integer(string='Thứ tự', default=10)
    is_published = fields.Boolean(string='Đã xuất bản', default=True)
