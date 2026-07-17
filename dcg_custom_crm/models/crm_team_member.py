# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmTeamMember(models.Model):
    _inherit = 'crm.team.member'

    commission_rate = fields.Float(string='Phần trăm hoa hồng (%)', default=lambda self: self._default_commission_rate())

    @api.model
    def _default_commission_rate(self):
        team_id = self.env.context.get('default_crm_team_id')
        if team_id:
            return self.env['crm.team'].browse(team_id).commission_rate
        return 2.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'commission_rate' not in vals and vals.get('crm_team_id'):
                vals['commission_rate'] = self.env['crm.team'].browse(vals['crm_team_id']).commission_rate
        return super().create(vals_list)
