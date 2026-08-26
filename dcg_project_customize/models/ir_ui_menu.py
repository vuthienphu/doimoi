# -*- coding: utf-8 -*-

from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _visible_menu_ids(self, debug=False):
        visible_ids = super()._visible_menu_ids(debug=debug)
        if not self.env.user.has_group(
            'dcg_project_customize.group_external_project_user'
        ):
            return visible_ids

        project_root = self.env.ref('project.menu_main_pm', raise_if_not_found=False)
        if not project_root:
            return visible_ids
        project_menu_ids = set(self.sudo().search([
            ('id', 'child_of', project_root.id),
        ]).ids)
        return visible_ids.intersection(project_menu_ids)
