# -*- coding: utf-8 -*-

from odoo import _, fields, models


class CrmTeamCommissionWizard(models.TransientModel):
    _name = 'crm.team.commission.wizard'
    _description = 'CRM Team Commission Update Wizard'

    team_id = fields.Many2one('crm.team', string='Bộ phận Sales', required=True, readonly=True)
    commission_rate = fields.Float(string='Phần trăm hoa hồng (%)', required=True, readonly=True)

    def action_confirm(self):
        self.ensure_one()
        members = self.team_id.crm_team_member_ids
        members.write({'commission_rate': self.commission_rate})
        message = _('Đã cập nhật hoa hồng cho %s thành viên.') % len(members)
        self.team_id.message_post(body=message)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Cập nhật hoa hồng'),
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
