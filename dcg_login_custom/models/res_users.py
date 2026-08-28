# -*- coding: utf-8 -*-
import logging

from odoo import api, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        _logger.info("=== OAuth Signin START ===")
        _logger.info("Provider: %s", provider)
        _logger.info("Validation: %s", validation)

        oauth_uid = validation['user_id']
        email = validation.get('email')

        _logger.info("OAuth UID: %s", oauth_uid)
        _logger.info("Email: %s", email)

        # 1. Existing OAuth user
        oauth_user = self.search([
            ('oauth_uid', '=', oauth_uid),
            ('oauth_provider_id', '=', provider)
        ], limit=1)

        _logger.info("Search by oauth_uid result: %s", oauth_user.ids)

        if oauth_user:
            _logger.info("Found existing OAuth user: %s", oauth_user.login)
            oauth_user.write({
                'oauth_access_token': params['access_token'],
            })
            _logger.info("=== OAuth Signin END (existing oauth user) ===")
            return oauth_user.login

        # 2. Existing user by email
        if email:
            existing = self.sudo().search([
                ('login', '=', email),
                ('active', '=', True),
            ], limit=1)

            _logger.info("Search by email result: %s", existing.ids)

            if existing:
                _logger.info("Link OAuth to existing user: %s", existing.login)

                existing.write({
                    'oauth_provider_id': provider,
                    'oauth_uid': oauth_uid,
                    'oauth_access_token': params['access_token'],
                })

                _logger.info("=== OAuth Signin END (linked existing user) ===")
                return existing.login

        # 3. Create new user
        _logger.info("No existing user found. Creating new user...")

        if self.env.context.get('no_user_creation'):
            _logger.warning("Context no_user_creation=True")
            return None

        if not email:
            _logger.error("Email is empty")
            raise AccessDenied()

        vals = {
            'name': validation.get('name', email),
            'login': email,
            'email': email,
            'oauth_provider_id': provider,
            'oauth_uid': oauth_uid,
            'oauth_access_token': params['access_token'],
            'active': True,
        }

        _logger.info("Create user vals: %s", vals)

        user = self.sudo().with_context(no_reset_password=True).create(vals)

        _logger.info("Created user id=%s login=%s", user.id, user.login)
        _logger.info("=== OAuth Signin END (new user) ===")

        return user.login

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("=== CREATE USER START ===")
        _logger.info("vals_list=%s", vals_list)

        default_password = self.env['ir.config_parameter'].sudo().get_param('dcg.default_user_password')
        if default_password:
            for vals in vals_list:
                if not vals.get('password'):
                    vals['password'] = default_password
                    _logger.info("Set default password from config parameter for user login=%s", vals.get('login'))

        users = super().create(vals_list)

        _logger.info("Created users=%s", users.ids)

        group_user = self.env.ref('base.group_user')
        for user in users:
            if not user.group_ids:
                user.sudo().write({'group_ids': [(4, group_user.id)]})
                _logger.info("Added default Internal User group to user=%s", user.login)
            _logger.info("Link employee for user=%s", user.login)
            self._link_or_create_employee(user)

        # OAuth signin chạy ở route auth='none' -> default_env của request KHÔNG có
        # user (env.user rỗng). Việc tạo hr.employee ở trên sinh avatar (binary ->
        # attachment) làm phát sinh recompute binary related field bị defer. Nếu để
        # tới lúc transaction.flush() cuối request, recompute đó chạy trên default_env
        # userless -> _get_group_ids() gọi ensure_one() trên res.users() rỗng -> nổ.
        # Flush ngay tại đây (đang ở env superuser) để drain recompute khi env.user hợp lệ.
        self.env.flush_all()

        _logger.info("=== CREATE USER END ===")

        return users

    def _link_or_create_employee(self, user):
        _logger.info("=== LINK EMPLOYEE START ===")

        email = user.email
        _logger.info("User=%s email=%s", user.login, email)

        if not email:
            _logger.warning("Email empty, skip employee")
            return

        Employee = self.env['hr.employee'].sudo()

        employee = Employee.search([
            ('work_email', '=', email)
        ], limit=1)

        if employee:
            _logger.info("Existing employee found id=%s", employee.id)
            if not employee.user_id:
                employee.user_id = user
                _logger.info("Linked employee to user")
        else:
            _logger.info("No existing employee found. Skipping employee creation.")

        _logger.info("=== LINK EMPLOYEE END ===")