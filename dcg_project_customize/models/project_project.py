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
        default_stages = self._get_dcg_default_task_stages()
        if default_stages:
            default_stages.write({'project_ids': [(4, project.id) for project in projects]})
        return projects

    @api.model
    def _get_dcg_default_task_stages(self):
        return self.env['project.task.type'].search([('is_dcg_default', '=', True)])

    @api.model
    def _dcg_assign_default_stages_to_all_projects(self):
        default_stages = self._get_dcg_default_task_stages()
        projects = self.search([])
        if default_stages and projects:
            default_stages.write({'project_ids': [(4, project.id) for project in projects]})
