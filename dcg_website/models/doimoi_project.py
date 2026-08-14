# -*- coding: utf-8 -*-

from odoo import fields, models


class DoimoiProject(models.Model):
    _name = 'doimoi.project'
    _description = 'Dự án tiêu biểu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    name = fields.Char(string='Tên dự án', required=True, tracking=True)
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    client_name = fields.Char(string='Khách hàng', required=True, tracking=True)
    industry_id = fields.Many2one('doimoi.industry', string='Ngành', tracking=True)
    summary = fields.Text(string='Mô tả ngắn', required=True, tracking=True)
    result = fields.Char(string='Kết quả nổi bật', tracking=True)
    image = fields.Image(string='Ảnh dự án', max_width=1200, max_height=800)
    project_url = fields.Char(string='Liên kết chi tiết', tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_featured = fields.Boolean(string='Nổi bật trên trang chủ', default=False, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)
