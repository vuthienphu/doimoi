# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    lead_id = fields.Many2one(
        'crm.lead',
        string='Cơ hội',
        readonly=True,
        copy=False,
        ondelete='set null',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            lead = self.env['crm.lead']
            lead_id = vals.get('lead_id') or self.env.context.get('default_lead_id')
            if lead_id:
                lead = self.env['crm.lead'].browse(lead_id).exists()
            if lead:
                vals.setdefault('lead_id', lead.id)
                vals.setdefault('partner_id', lead.partner_id.id)
                vals.setdefault('user_id', lead.user_id.id)

        projects = super().create(vals_list)
        if projects:
            self.env['project.task.type']._dcg_standard_stages().write({
                'project_ids': [(4, project.id) for project in projects],
            })
        return projects

    @api.model
    def _dcg_assign_all_stages_to_all_projects(self):
        projects = self.with_context(active_test=False).search([])
        stages = self.env['project.task.type']._dcg_standard_stages()
        if projects and stages:
            stages.write({'project_ids': [(4, project.id) for project in projects]})
