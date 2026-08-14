# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class DoimoiServiceGroup(models.Model):
    _name = 'doimoi.service.group'
    _description = 'Nhóm Dịch vụ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Tên nhóm', required=True, tracking=True)
    title = fields.Char(string='Tiêu đề chính (Hiển thị trang chủ)', tracking=True)
    subtitle = fields.Text(string='Mô tả phụ', tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)


class DoimoiService(models.Model):
    _name = 'doimoi.service'
    _description = 'Dịch vụ / Giải pháp'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Tên dịch vụ', required=True, tracking=True)
    website_id = fields.Many2one('website', string='Website', index=True, tracking=True)
    service_group_id = fields.Many2one('doimoi.service.group', string='Nhóm dịch vụ', required=True, tracking=True)
    icon = fields.Image(string='Icon dịch vụ', max_width=256, max_height=256)
    short_description = fields.Text(string='Mô tả ngắn', tracking=True)
    features = fields.Text(string='Các tính năng (mỗi dòng 1 tính năng)', tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_published = fields.Boolean(string='Đã xuất bản', default=False, tracking=True)

    @api.constrains('is_published', 'icon', 'short_description')
    def _check_publish_content(self):
        for service in self:
            if service.is_published and (not service.icon or not service.short_description):
                raise ValidationError(_(
                    'Dịch vụ phải có Icon và Mô tả ngắn trước khi xuất bản.'
                ))
