# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MobileDeviceToken(models.Model):
    _name = 'mobile.device.token'
    _description = 'Thiết bị & FCM Token của Người dùng'
    _order = 'last_login desc, id desc'

    name = fields.Char(string='Tên hiển thị', compute='_compute_name', store=True)
    user_id = fields.Many2one(
        'res.users',
        string='Người dùng',
        required=True,
        ondelete='cascade',
        index=True,
    )
    token = fields.Char(
        string='FCM Device Token',
        required=True,
        index=True,
        help='Token định danh thiết bị do Firebase Cloud Messaging cấp',
    )
    device_id = fields.Char(
        string='Mã định danh thiết bị (Device ID)',
        index=True,
        help='Hardware UUID hoặc ID thiết bị từ phía App',
    )
    device_name = fields.Char(
        string='Tên thiết bị / Dòng máy',
        help='Ví dụ: iPhone 15 Pro, Samsung Galaxy S24, Pixel 8',
    )
    platform = fields.Selection([
        ('ios', 'iOS (Apple)'),
        ('android', 'Android'),
        ('web', 'Web Browser'),
    ], string='Nền tảng', default='android', required=True)

    app_version = fields.Char(string='Phiên bản App')
    is_active = fields.Boolean(
        string='Đang hoạt động',
        default=True,
        help='Token sẽ chuyển thành False khi người dùng đăng xuất hoặc khi Firebase báo token không còn hợp lệ',
    )
    last_login = fields.Datetime(
        string='Đăng nhập lần cuối',
        default=fields.Datetime.now,
    )
    login_history_ids = fields.One2many(
        'mobile.login.history',
        'device_token_id',
        string='Lịch sử đăng nhập',
    )
    login_count = fields.Integer(
        string='Số lần đăng nhập',
        compute='_compute_login_count',
    )

    _sql_constraints = [
        ('token_uniq', 'unique(token)', 'FCM Device Token này đã tồn tại trong hệ thống!'),
    ]

    @api.depends('user_id.name', 'device_name', 'platform')
    def _compute_name(self):
        for record in self:
            dev = record.device_name or record.platform or 'Thiết bị'
            user = record.user_id.name if record.user_id else 'Chưa gán'
            record.name = f"{user} - {dev}"

    @api.depends('login_history_ids')
    def _compute_login_count(self):
        for record in self:
            record.login_count = len(record.login_history_ids)

    def action_deactivate(self):
        self.write({'is_active': False})

    def action_activate(self):
        self.write({'is_active': True})
