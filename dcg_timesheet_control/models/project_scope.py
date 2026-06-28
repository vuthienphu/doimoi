# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgProjectScope(models.Model):
    _inherit = 'dcg.project.scope'

    ts_actual_hours = fields.Float(
        compute='_compute_ts_hours', store=True, string='Actual Hours (TS)',
    )
    ts_billable_hours = fields.Float(
        compute='_compute_ts_hours', store=True, string='Billable Hours (TS)',
    )
    ts_non_billable_hours = fields.Float(
        compute='_compute_ts_hours', store=True, string='Non-billable (TS)',
    )
    ts_ot_hours = fields.Float(
        compute='_compute_ts_hours', store=True, string='OT Hours (TS)',
    )
    ts_line_count = fields.Integer(
        compute='_compute_ts_hours', string='TS Lines',
    )

    def _compute_ts_hours(self):
        Line = self.env['account.analytic.line']
        for rec in self:
            domain = [
                ('dcg_scope_id', '=', rec.id),
                ('line_state', '=', 'approved'),
            ]
            lines = Line.search(domain)
            rec.ts_line_count = len(lines)
            rec.ts_actual_hours = sum(lines.mapped('unit_amount'))
            rec.ts_billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type == 'billable'
            )
            rec.ts_non_billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type != 'billable'
            )
            rec.ts_ot_hours = sum(
                l.overtime_hours or l.unit_amount for l in lines if l.is_overtime
            )
