# -*- coding: utf-8 -*-

from odoo import fields, models

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    commission_rate = fields.Float(string='Phần trăm hoa hồng (%)', default=2.0)

    def action_open_commission_update_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cập nhật toàn bộ hoa hồng',
            'res_model': 'crm.team.commission.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_team_id': self.id,
                'default_commission_rate': self.commission_rate,
            },
        }
