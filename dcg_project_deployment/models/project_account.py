# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectAccount(models.Model):
    _name = 'project.account'
    _description = 'Tài khoản dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project_id, name'

    project_id = fields.Many2one('project.project', string='Dự án', required=True, tracking=True, ondelete='cascade')
    name = fields.Char(string='Tên tài khoản', required=True)
    account_type = fields.Selection([
        ('admin', 'Quản trị viên'),
        ('test', 'Kiểm thử'),
        ('user', 'Người dùng'),
        ('readonly', 'Chỉ đọc'),
        ('api', 'API'),
        ('database', 'Cơ sở dữ liệu'),
        ('ftp', 'FTP'),
        ('email', 'Thư điện tử'),
        ('other', 'Khác'),
    ], string='Loại tài khoản', default='other', tracking=True)
    username = fields.Char(string='Tên đăng nhập')
    password = fields.Char(string='Mật khẩu', groups='base.group_system')
    password_masked = fields.Char(string='Mật khẩu đã che', compute='_compute_password_masked')
    url = fields.Char(string='Đường dẫn truy cập')
    note = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Đang hoạt động', default=True)

    # TODO: Mã hóa mật khẩu trước khi lưu; khóa phải lấy từ biến môi trường hoặc ir.config_parameter.

    @api.depends('password')
    def _compute_password_masked(self):
        for account in self:
            if self.env.user.has_group('base.group_system'):
                account.password_masked = account.password
            else:
                account.password_masked = '***' if account.sudo().password else False
