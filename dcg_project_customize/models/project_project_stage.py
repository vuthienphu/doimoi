# -*- coding: utf-8 -*-

from odoo import api, models


class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    @api.model
    def _dcg_open_all_project_stages(self):
        self.with_context(active_test=False).search([('fold', '=', True)]).write({'fold': False})
