# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgProjectDelivery(models.Model):
    _inherit = 'dcg.project.delivery'

    timesheet_line_count = fields.Integer(
        compute='_compute_timesheet_totals', string='Timesheet Lines',
    )
    total_actual_hours = fields.Float(
        compute='_compute_timesheet_totals', store=True, string='Actual Hours (approved)',
    )
    total_billable_hours = fields.Float(
        compute='_compute_timesheet_totals', store=True, string='Billable Hours',
    )
    total_non_billable_hours = fields.Float(
        compute='_compute_timesheet_totals', store=True, string='Non-billable Hours',
    )
    total_ot_hours = fields.Float(
        compute='_compute_timesheet_totals', store=True, string='OT Hours',
    )

    @api.depends('scope_ids.ts_actual_hours', 'scope_ids.ts_billable_hours',
                 'scope_ids.ts_non_billable_hours', 'scope_ids.ts_ot_hours')
    def _compute_timesheet_totals(self):
        Line = self.env['account.analytic.line']
        for rec in self:
            domain = [
                ('dcg_project_id', '=', rec.id),
                ('line_state', '=', 'approved'),
            ]
            lines = Line.search(domain)
            rec.timesheet_line_count = len(lines)
            rec.total_actual_hours = sum(lines.mapped('unit_amount'))
            rec.total_billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type == 'billable'
            )
            rec.total_non_billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type != 'billable'
            )
            rec.total_ot_hours = sum(
                l.overtime_hours or l.unit_amount for l in lines if l.is_overtime
            )

    def action_view_timesheet_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Timesheet Lines',
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'domain': [('dcg_project_id', '=', self.id)],
            'context': {'default_dcg_project_id': self.id},
        }
