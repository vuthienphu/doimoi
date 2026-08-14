# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DoimoiSiteSettings(models.Model):
    _name = 'doimoi.site.settings'
    _description = 'Cấu hình Header và Footer dùng chung'

    name = fields.Char(string='Tên cấu hình', required=True, default='Header & Footer')
    website_id = fields.Many2one('website', string='Website áp dụng', index=True)
    use_custom_header_logo = fields.Boolean(string='Dùng logo Header tùy chỉnh', default=False)
    header_logo = fields.Image(string='Logo Header', max_width=800, max_height=300)
    use_custom_footer_logo = fields.Boolean(string='Dùng logo Footer tùy chỉnh', default=False)
    footer_logo = fields.Image(string='Logo Footer', max_width=800, max_height=300)
    home_label = fields.Char(string='Trang chủ', required=True)
    home_url = fields.Char(string='URL Trang chủ', required=True)
    solutions_label = fields.Char(string='Giải pháp', required=True)
    solutions_url = fields.Char(string='URL Giải pháp', required=True)
    industries_label = fields.Char(string='Ngành', required=True)
    industries_url = fields.Char(string='URL Ngành', required=True)
    about_label = fields.Char(string='Về Đổi Mới', required=True)
    about_url = fields.Char(string='URL Về Đổi Mới', required=True)
    contact_label = fields.Char(string='Liên hệ', required=True)
    contact_url = fields.Char(string='URL Liên hệ', required=True)
    header_cta_label = fields.Char(string='Nhãn nút tư vấn', required=True)
    header_cta_url = fields.Char(string='URL nút tư vấn', required=True)
    footer_description = fields.Text(string='Mô tả thương hiệu')
    address = fields.Text(string='Địa chỉ')
    phone = fields.Char(string='Điện thoại')
    email = fields.Char(string='Email')
    website_url = fields.Char(string='Website')
    location = fields.Char(string='Khu vực')
    facebook_url = fields.Char(string='Facebook')
    linkedin_url = fields.Char(string='LinkedIn')
    youtube_url = fields.Char(string='YouTube')
    privacy_label = fields.Char(string='Nhãn chính sách bảo mật')
    privacy_url = fields.Char(string='URL chính sách bảo mật')
    terms_label = fields.Char(string='Nhãn điều khoản')
    terms_url = fields.Char(string='URL điều khoản')
    copyright_name = fields.Char(string='Tên hiển thị Copyright')

    @api.constrains('website_id')
    def _check_one_settings_per_website(self):
        for record in self:
            domain = [('id', '!=', record.id), ('website_id', '=', record.website_id.id or False)]
            if self.search_count(domain):
                raise ValidationError(_('Mỗi website chỉ được có một cấu hình Header & Footer.'))
