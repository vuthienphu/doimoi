# -*- coding: utf-8 -*-
from odoo import fields, models


class MobileLoginHistory(models.Model):
    _name = 'mobile.login.history'
    _description = 'Lịch sử Đăng nhập App của Thiết bị'
    _order = 'login_time desc, id desc'

    user_id = fields.Many2one(
        'res.users',
        string='Người dùng Odoo',
        ondelete='set null',
        index=True,
    )
    email_attempted = fields.Char(
        string='Email dùng để đăng nhập',
        index=True,
    )
    device_token_id = fields.Many2one(
        'mobile.device.token',
        string='Thiết bị',
        ondelete='set null',
    )
    device_name = fields.Char(string='Tên thiết bị')
    device_id = fields.Char(string='Mã định danh thiết bị')
    platform = fields.Selection([
        ('ios', 'iOS (Apple)'),
        ('android', 'Android'),
        ('web', 'Web Browser'),
    ], string='Nền tảng')

    app_version = fields.Char(string='Phiên bản App')
    ip_address = fields.Char(string='Địa chỉ IP')
    user_agent = fields.Char(string='User Agent')
    login_time = fields.Datetime(
        string='Thời điểm',
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    status = fields.Selection([
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('revoked', 'Đã đăng xuất'),
    ], string='Trạng thái', default='success', required=True)

    failure_reason = fields.Char(string='Lý do thất bại / Ghi chú')
