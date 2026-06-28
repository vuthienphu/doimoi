# -*- coding: utf-8 -*-
from odoo import _, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    contract_count = fields.Integer(compute='_compute_contract_count', string='Contracts')
    primary_contract_id = fields.Many2one('dcg.contract', string='Primary Contract', copy=False)

    def _compute_contract_count(self):
        Contract = self.env['dcg.contract']
        for rec in self:
            rec.contract_count = Contract.search_count([('lead_id', '=', rec.id)]) if rec.id else 0

    def action_view_contracts(self):
        self.ensure_one()
        contracts = self.env['dcg.contract'].search([('lead_id', '=', self.id)])
        if len(contracts) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'dcg.contract',
                'res_id': contracts.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts'),
            'res_model': 'dcg.contract',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id, 'default_partner_id': self.partner_id.id},
        }
