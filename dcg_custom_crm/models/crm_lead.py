# -*- coding: utf-8 -*-

from markupsafe import Markup

from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    commission_rate = fields.Float(
        string='Phần trăm hoa hồng (%)',
        compute='_compute_commission_rate',
        store=True,
        readonly=True,
    )
    other_ids = fields.Many2many(
        'res.partner',
        'crm_lead_other_partner_rel',
        'lead_id',
        'partner_id',
        string='Người liên hệ khác',
        domain=[('is_company', '=', False)],
    )
    survey_note = fields.Text(string='Ghi chú khảo sát')
    estimate_attachment_ids = fields.Many2many(
        'ir.attachment',
        'crm_lead_estimate_attachment_rel',
        'lead_id',
        'attachment_id',
        string='File ước tính công việc',
    )
    survey_done = fields.Boolean(string='Đã khảo sát', default=False)
    survey_finish_date = fields.Datetime(string='Ngày hoàn thành khảo sát', readonly=True)
    demo_done = fields.Boolean(string='Đã demo', default=False)
    demo_finish_date = fields.Datetime(string='Ngày hoàn thành demo', readonly=True)
    project_id = fields.Many2one('project.project', string='Link dự án', copy=False, invisible = "1")

    @api.depends(
        'team_id',
        'user_id',
        'team_id.crm_team_member_ids.active',
        'team_id.crm_team_member_ids.commission_rate',
        'team_id.crm_team_member_ids.user_id',
    )
    def _compute_commission_rate(self):
        TeamMember = self.env['crm.team.member']
        for lead in self:
            member = TeamMember.search([
                ('crm_team_id', '=', lead.team_id.id),
                ('user_id', '=', lead.user_id.id),
                ('active', '=', True),
            ], limit=1)
            lead.commission_rate = member.commission_rate if member else 0.0

    def action_complete_survey(self):
        now = fields.Datetime.now()
        for lead in self:
            lead.write({
                'survey_done': True,
                'survey_finish_date': now,
            })
            lead.message_post(body=_('Đã hoàn thành khảo sát ngày %s.') % fields.Datetime.to_string(now))
        return True

    def action_continue_survey(self):
        self.ensure_one()
        return self._action_open_survey_wizard('survey')

    def action_complete_demo(self):
        now = fields.Datetime.now()
        for lead in self:
            lead.write({
                'demo_done': True,
                'demo_finish_date': now,
            })
            lead.message_post(body=_('Đã hoàn thành demo ngày %s.') % fields.Datetime.to_string(now))
        return True

    def action_continue_demo(self):
        self.ensure_one()
        return self._action_open_survey_wizard('demo')

    def _action_open_survey_wizard(self, wizard_type):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tiếp tục khảo sát') if wizard_type == 'survey' else _('Tiếp tục demo'),
            'res_model': 'crm.survey.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_type': wizard_type,
            },
        }

    def write(self, vals):
        result = super().write(vals)
        if {'stage_id', 'probability'} & set(vals):
            self._create_project_for_won_opportunities()
        return result

    def action_set_won(self):
        result = super().action_set_won()
        self._create_project_for_won_opportunities()
        return result

    def action_set_won_rainbowman(self):
        result = super().action_set_won_rainbowman()
        self._create_project_for_won_opportunities()
        return result

    def _create_project_for_won_opportunities(self):
        Project = self.env['project.project']
        won_leads = self.filtered(
            lambda lead: lead.type == 'opportunity'
            and not lead.project_id
            and (lead.probability >= 100 or lead.stage_id.is_won)
        )
        for lead in won_leads:
            project = Project.create({
                'name': lead.name,
                'partner_id': lead.partner_id.id,
                'user_id': lead.user_id.id,
                'x_lead_id': lead.id,
            })
            lead.project_id = project
            lead.message_post(
                body=Markup(_('Dự án <b>%s</b> đã được tạo liên kết với Cơ hội này.')) % project.display_name
            )
