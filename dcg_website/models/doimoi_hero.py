# -*- coding: utf-8 -*-

from odoo import fields, models


class DoimoiHero(models.Model):
    _name = 'doimoi.hero'
    _description = 'Banner và CTA theo trang'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Tên nội bộ', required=True, tracking=True)
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    page = fields.Selection([
        ('home', 'Trang chủ'),
        ('solutions', 'Giải pháp'),
        ('industries', 'Ngành'),
        ('projects', 'Dự án'),
        ('about', 'Về Đổi Mới'),
        ('contact', 'Liên hệ'),
    ], string='Trang áp dụng', required=True, default='home', tracking=True)
    eyebrow = fields.Char(string='Nhãn nhỏ', required=True, tracking=True)
    title = fields.Char(string='Tiêu đề', required=True, tracking=True)
    highlighted_text = fields.Char(
        string='Cụm từ nhấn mạnh',
        help='Nếu cụm từ này xuất hiện trong tiêu đề, frontend sẽ tô màu cam.',
    )
    subtitle = fields.Text(string='Mô tả', required=True, tracking=True)
    image = fields.Image(
        string='Ảnh banner',
        max_width=1600,
        max_height=1200,
    )
    visual_mode = fields.Selection([
        ('image', 'Ảnh banner'),
        ('dashboard', 'Dashboard minh họa'),
    ], string='Kiểu hiển thị bên phải', default='image', required=True, tracking=True)
    dashboard_eyebrow = fields.Char(string='Nhãn dashboard')
    dashboard_title = fields.Char(string='Tiêu đề dashboard')
    metric_1_label = fields.Char(string='KPI 1 - Nhãn')
    metric_1_value = fields.Char(string='KPI 1 - Giá trị')
    metric_1_trend = fields.Char(string='KPI 1 - Xu hướng')
    metric_2_label = fields.Char(string='KPI 2 - Nhãn')
    metric_2_value = fields.Char(string='KPI 2 - Giá trị')
    metric_2_trend = fields.Char(string='KPI 2 - Xu hướng')
    metric_3_label = fields.Char(string='KPI 3 - Nhãn')
    metric_3_value = fields.Char(string='KPI 3 - Giá trị')
    metric_3_trend = fields.Char(string='KPI 3 - Xu hướng')
    chart_title = fields.Char(string='Tiêu đề biểu đồ')
    status_1 = fields.Char(string='Trạng thái 1')
    status_2 = fields.Char(string='Trạng thái 2')
    primary_button_label = fields.Char(string='Nút chính', required=True, tracking=True)
    primary_button_url = fields.Char(string='Liên kết nút chính', required=True, tracking=True)
    secondary_button_label = fields.Char(string='Nút phụ', tracking=True)
    secondary_button_url = fields.Char(string='Liên kết nút phụ', tracking=True)
    cta_title = fields.Char(string='Tiêu đề CTA', tracking=True)
    cta_subtitle = fields.Text(string='Mô tả CTA', tracking=True)
    cta_button_label = fields.Char(string='Nhãn nút CTA', tracking=True)
    cta_button_url = fields.Char(string='Liên kết CTA', tracking=True)
    show_cta = fields.Boolean(string='Hiển thị CTA', default=True, tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)
    seo_title = fields.Char(string='SEO Title', tracking=True)
    seo_description = fields.Text(string='Meta Description', tracking=True)
    seo_keywords = fields.Char(string='Meta Keywords', tracking=True)
    seo_image = fields.Image(string='Ảnh chia sẻ SEO', max_width=1200, max_height=630)
