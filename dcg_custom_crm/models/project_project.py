# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_lead_id = fields.Many2one('crm.lead', string='Cơ hội', readonly=True, copy=False, ondelete='set null')
