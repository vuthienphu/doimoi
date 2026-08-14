# -*- coding: utf-8 -*-

from odoo import api, models, fields

class DoimoiClient(models.Model):
    _name = 'doimoi.client'
    _description = 'Khách hàng tiêu biểu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Tên khách hàng', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Liên hệ / Công ty', tracking=True, ondelete='set null')
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    short_name = fields.Char(string='Tên viết tắt (Icon)', help="VD: VNPT, TKH...", tracking=True)
    industry = fields.Char(string='Ngành nghề', help="Ví dụ: Viễn thông, Khai khoáng...", tracking=True)
    logo = fields.Image(string='Logo', max_width=512, max_height=512)
    website_url = fields.Char(string='Website URL', tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.name
            self.website_url = self.partner_id.website or self.website_url
            self.logo = self.partner_id.image_512 or self.logo
