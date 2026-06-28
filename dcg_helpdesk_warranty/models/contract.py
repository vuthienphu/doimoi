# -*- coding: utf-8 -*-
from odoo import _, fields, models


class DcgContract(models.Model):
    _inherit = 'dcg.contract'

    ticket_count = fields.Integer(compute='_compute_ticket_count')

    def _compute_ticket_count(self):
        Ticket = self.env['dcg.warranty.ticket']
        for rec in self:
            rec.ticket_count = Ticket.search_count(
                [('contract_id', '=', rec.id)]
            ) if rec.id else 0

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Warranty Tickets'),
            'res_model': 'dcg.warranty.ticket',
            'view_mode': 'list,kanban,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {
                'default_contract_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }
