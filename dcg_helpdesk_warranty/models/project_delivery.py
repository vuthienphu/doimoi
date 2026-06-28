# -*- coding: utf-8 -*-
from odoo import _, fields, models


class DcgProjectDelivery(models.Model):
    _inherit = 'dcg.project.delivery'

    ticket_count = fields.Integer(compute='_compute_ticket_count')

    def _compute_ticket_count(self):
        Ticket = self.env['dcg.warranty.ticket']
        for rec in self:
            rec.ticket_count = Ticket.search_count(
                [('project_id', '=', rec.id)]
            ) if rec.id else 0

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Warranty Tickets'),
            'res_model': 'dcg.warranty.ticket',
            'view_mode': 'list,kanban,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_contract_id': self.contract_id.id,
                'default_partner_id': self.partner_id.id,
            },
        }
