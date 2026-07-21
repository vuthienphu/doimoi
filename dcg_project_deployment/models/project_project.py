# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import AccessError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    account_ids = fields.One2many(
        'project.account',
        'project_id',
        string='Tài khoản',
        groups='project.group_project_manager,base.group_system',
    )
    remote_ids = fields.One2many(
        'project.remote',
        'project_id',
        string='Kết nối máy chủ',
        groups='base.group_system',
    )
    account_count = fields.Integer(
        string='Số tài khoản',
        compute='_compute_account_count',
        groups='project.group_project_manager,base.group_system',
    )
    remote_count = fields.Integer(
        string='Số kết nối',
        compute='_compute_remote_count',
        groups='base.group_system',
    )

    def _compute_account_count(self):
        Account = self.env['project.account'].with_context(active_test=False)
        for project in self:
            project.account_count = Account.search_count([('project_id', '=', project.id)])

    def _compute_remote_count(self):
        Remote = self.env['project.remote'].with_context(active_test=False)
        for project in self:
            project.remote_count = Remote.search_count([('project_id', '=', project.id)])

    def action_open_project_accounts(self):
        self.ensure_one()
        if not (
            self.env.user.has_group('project.group_project_manager')
            or self.env.user.has_group('base.group_system')
        ):
            raise AccessError(_('Bạn không có quyền xem tài khoản triển khai của dự án.'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tài khoản dự án',
            'res_model': 'project.account',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id, 'active_test': False},
        }

    def action_open_project_remotes(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_('Bạn không có quyền xem thông tin kết nối máy chủ của dự án.'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kết nối máy chủ',
            'res_model': 'project.remote',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id, 'active_test': False},
        }
