# -*- coding: utf-8 -*-
from odoo import _, fields, models


class DcgProjectDelivery(models.Model):
    _inherit = 'dcg.project.delivery'

    trip_count = fields.Integer(compute='_compute_trip_count', string='Trips')
    total_trip_cost = fields.Monetary(
        compute='_compute_trip_count', store=False,
        string='Trip Cost', currency_field='currency_id',
    )

    def _compute_trip_count(self):
        Trip = self.env['dcg.business.trip']
        for rec in self:
            trips = Trip.search([('project_id', '=', rec.id)])
            rec.trip_count = len(trips)
            rec.total_trip_cost = sum(trips.mapped('actual_cost'))

    def action_view_trips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Business Trips'),
            'res_model': 'dcg.business.trip',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
