# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_count = fields.Integer(compute='_compute_contract_count', string='Contracts')
    contract_created = fields.Boolean(string='Contract Created', copy=False)

    def _compute_contract_count(self):
        Contract = self.env['dcg.contract']
        for rec in self:
            rec.contract_count = Contract.search_count([('quotation_id', '=', rec.id)]) if rec.id else 0

    def action_create_contract(self):
        """Tạo dcg.contract từ quotation — map header + estimate lines nếu có."""
        self.ensure_one()
        lead = self.env['crm.lead'].search([
            ('id', '=', self.opportunity_id.id)
        ], limit=1) if self.opportunity_id else self.env['crm.lead']

        estimate = lead.approved_estimate_id or lead.latest_estimate_id if lead else False

        vals = {
            'partner_id': self.partner_id.id,
            'quotation_id': self.id,
            'lead_id': lead.id if lead else False,
            'estimate_id': estimate.id if estimate else False,
            'currency_id': self.currency_id.id,
            'amount_total': self.amount_total,
            'amount_untaxed': self.amount_untaxed,
            'tax_amount': self.amount_tax,
            'account_manager_id': (lead.account_manager_id.id if lead and lead.account_manager_id else self.user_id.id),
            'presales_owner_id': lead.presales_owner_id.id if lead and lead.presales_owner_id else False,
            'scope_summary': lead.solution_scope_summary if lead else '',
            'handover_note': lead.handover_note if lead else '',
            'expected_cost': estimate.estimated_cost if estimate else 0.0,
        }
        contract = self.env['dcg.contract'].create(vals)

        # Map estimate lines → contract lines
        if estimate and estimate.line_ids:
            ContractLine = self.env['dcg.contract.line']
            for eline in estimate.line_ids:
                ContractLine.create({
                    'contract_id': contract.id,
                    'name': eline.name,
                    'service_catalog_id': eline.service_catalog_id.id if eline.service_catalog_id else False,
                    'scope_id': eline.scope_id.id if eline.scope_id else False,
                    'estimate_line_id': eline.id,
                    'quantity': 1.0,
                    'unit_price': eline.revenue_amount or 0.0,
                    'ba_hours': eline.ba_hours,
                    'dev_hours': eline.dev_hours,
                    'test_hours': eline.test_hours,
                    'pm_hours': eline.pm_hours,
                    'support_hours': eline.support_hours,
                })

        self.write({'contract_created': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.contract',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts'),
            'res_model': 'dcg.contract',
            'view_mode': 'list,form',
            'domain': [('quotation_id', '=', self.id)],
        }
