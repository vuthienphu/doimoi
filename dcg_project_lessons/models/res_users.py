# -*- coding: utf-8 -*-

from odoo import Command, api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _apply_dcg_default_user_access(self):
        internal_group = self.env.ref('base.group_user')
        lesson_group = self.env.ref('dcg_project_lessons.group_project_lesson_employee')
        users = self.sudo().with_context(active_test=False).search([
            ('active', '=', True),
            ('share', '=', False),
            ('group_ids', 'in', internal_group.id),
        ])
        for user in users:
            user.write({'group_ids': [Command.link(lesson_group.id)]})
        return True
