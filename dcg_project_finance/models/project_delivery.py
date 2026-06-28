# -*- coding: utf-8 -*-
from odoo import _, fields, models


class DcgProjectDelivery(models.Model):
    _inherit = 'dcg.project.delivery'

    finance_id = fields.Many2one(
        'dcg.project.finance', string='Finance Record', copy=False,
    )

    def action_view_finance(self):
        self.ensure_one()
        if self.finance_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'dcg.project.finance',
                'res_id': self.finance_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return self.action_create_finance()

    def action_create_finance(self):
        """Auto-create finance record from project (spec mục 43)."""
        self.ensure_one()
        Finance = self.env['dcg.project.finance']
        if self.finance_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'dcg.project.finance',
                'res_id': self.finance_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        finance = Finance.create({
            'project_id': self.id,
            'contract_id': self.contract_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'lead_id': self.lead_id.id if self.lead_id else False,
            'estimate_id': self.estimate_id.id if self.estimate_id else False,
            'quotation_id': self.quotation_id.id if self.quotation_id else False,
            'project_manager_id': self.project_manager_id.id if self.project_manager_id else False,
            'delivery_owner_id': self.delivery_owner_id.id if self.delivery_owner_id else False,
            'planned_revenue': self.contract_amount_total,
            'planned_cost': self.expected_cost,
            'planned_hours': self.planned_effort_hours,
        })
        self.write({'finance_id': finance.id})
        # Sync revenue lines from contract payments
        finance.action_sync_revenue_from_contract()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.project.finance',
            'res_id': finance.id,
            'view_mode': 'form',
            'target': 'current',
        }
