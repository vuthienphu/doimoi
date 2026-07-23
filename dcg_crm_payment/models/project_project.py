# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    contract_id = fields.Many2one('crm.contract', string='Hợp đồng')

    @api.model_create_multi
    def create(self, vals_list):
        projects = super(ProjectProject, self).create(vals_list)
        for project in projects:
            # Nếu dự án được sinh ra từ Cơ hội và Cơ hội đó có Hợp đồng,
            # tự động liên kết dự án với hợp đồng.
            if project.lead_id and project.lead_id.contract_id:
                contract = project.lead_id.contract_id
                project.contract_id = contract.id
                contract.project_id = project.id
        return projects

    def action_view_lead(self):
        self.ensure_one()
        if not self.lead_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cơ hội',
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
