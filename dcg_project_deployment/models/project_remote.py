# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectRemote(models.Model):
    _name = 'project.remote'
    _description = 'Kết nối máy chủ dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project_id, name'

    project_id = fields.Many2one('project.project', string='Dự án', required=True, tracking=True, ondelete='cascade')
    name = fields.Char(string='Tên kết nối', required=True)
    server_type = fields.Selection([
        ('linux', 'Linux'),
        ('windows', 'Máy chủ Windows'),
        ('nas', 'NAS'),
        ('docker', 'Docker'),
        ('cloud', 'Đám mây'),
        ('other', 'Khác'),
    ], string='Loại máy chủ', default='linux')
    connection_type = fields.Selection([
        ('ssh', 'SSH'),
        ('rdp', 'RDP'),
        ('ultraviewer', 'UltraViewer'),
        ('anydesk', 'AnyDesk'),
        ('teamviewer', 'TeamViewer'),
        ('webpanel', 'Bảng điều khiển máy chủ web'),
        ('ftp', 'FTP'),
        ('sftp', 'SFTP'),
        ('database', 'Cơ sở dữ liệu'),
        ('vpn', 'VPN'),
        ('other', 'Khác'),
    ], string='Phương thức kết nối', required=True, default='ssh', tracking=True)
    host = fields.Char(string='Máy chủ / IP')
    port = fields.Integer(string='Cổng')
    username = fields.Char(string='Tên đăng nhập')
    password = fields.Char(string='Mật khẩu', groups='base.group_system')
    private_key = fields.Text(string='Khóa riêng', groups='base.group_system')
    path = fields.Char(string='Đường dẫn')
    url = fields.Char(string='Đường dẫn truy cập')
    partner_id_field = fields.Char(string='Mã đối tác')
    address_field = fields.Char(string='Địa chỉ / ID')
    database = fields.Char(string='Cơ sở dữ liệu')
    note = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Đang hoạt động', default=True)

    # TODO: Mã hóa mật khẩu/khóa riêng trước khi lưu vào cơ sở dữ liệu.
