# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CrmSurveyWizard(models.TransientModel):
    _name = 'crm.survey.wizard'
    _description = 'CRM Survey and Demo Follow-up Wizard'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True)
    type = fields.Selection(
        [('survey', 'Khảo sát'), ('demo', 'Demo')],
        string='Loại',
        required=True,
    )
    content = fields.Text(string='Nội dung', required=True)
    date_from = fields.Date(string='Từ ngày', required=True)
    date_to = fields.Date(string='Đến ngày', required=True)

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_to < wizard.date_from:
                raise exceptions.ValidationError(_('Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.'))

    def action_confirm(self):
        self.ensure_one()
        label = _('Khảo sát thêm') if self.type == 'survey' else _('Demo thêm')
        self.lead_id.message_post(
            body=_('%(label)s: %(content)s - Từ %(date_from)s đến %(date_to)s.') % {
                'label': label,
                'content': self.content,
                'date_from': self.date_from,
                'date_to': self.date_to,
            }
        )
        return {'type': 'ir.actions.act_window_close'}
