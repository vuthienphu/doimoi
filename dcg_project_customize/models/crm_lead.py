# -*- coding: utf-8 -*-

from markupsafe import Markup

from odoo import _, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_id = fields.Many2one(
        'project.project',
        string='Link dự án',
        readonly=True,
        copy=False,
        ondelete='set null',
    )

    def write(self, vals):
        result = super().write(vals)
        if {'stage_id', 'probability'} & set(vals):
            self._dcg_create_project_for_won_opportunities()
        return result

    def action_set_won(self):
        result = super().action_set_won()
        self._dcg_create_project_for_won_opportunities()
        return result

    def action_set_won_rainbowman(self):
        result = super().action_set_won_rainbowman()
        self._dcg_create_project_for_won_opportunities()
        return result

    def _dcg_create_project_for_won_opportunities(self):
        Project = self.env['project.project']
        for lead in self.filtered(lambda item: item.type == 'opportunity' and (item.probability >= 100 or item.stage_id.is_won)):
            project = Project.browse()
            if lead.project_id:
                project = lead.project_id
                if not project.lead_id:
                    project.lead_id = lead

            if not project:
                project = Project.search([('lead_id', '=', lead.id)], limit=1)

            if not project:
                project = Project.create({
                    'name': lead.name,
                    'lead_id': lead.id,
                    'partner_id': lead.partner_id.id,
                    'user_id': lead.user_id.id,
                })
                lead.message_post(
                    body=Markup(_('Dự án <b>%s</b> đã được tạo từ cơ hội này.')) % project.display_name
                )

            if not lead.project_id:
                lead.project_id = project

    def action_open_dcg_project_tasks(self):
        self.ensure_one()
        if not self.project_id:
            self._dcg_create_project_for_won_opportunities()
        project = self.project_id
        if not project:
            return False

        action = self.env['ir.actions.actions']._for_xml_id('project.action_view_task')
        action.update({
            'name': project.display_name,
            'display_name': project.display_name,
            'domain': [
                ('project_id', '=', project.id),
                ('has_template_ancestor', '=', False),
            ],
            'context': {
                'default_project_id': project.id,
                'active_id': project.id,
                'active_model': 'project.project',
                'search_default_project_id': project.id,
            },
            'target': 'main',
        })
        return action
