# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta


class DcgGenerateSheetWizard(models.TransientModel):
    _name = 'dcg.generate.sheet.wizard'
    _description = 'Generate Timesheet Sheet'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        default=lambda self: self.env.user.employee_id,
    )
    period_type = fields.Selection(
        [('weekly', 'Weekly'), ('monthly', 'Monthly')],
        string='Period', required=True, default='weekly',
    )
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    @api.onchange('period_type', 'date_start')
    def _onchange_period(self):
        if self.date_start and self.period_type == 'weekly':
            # Snap to Monday–Sunday
            weekday = self.date_start.weekday()
            monday = self.date_start - timedelta(days=weekday)
            self.date_start = monday
            self.date_end = monday + timedelta(days=6)
        elif self.date_start and self.period_type == 'monthly':
            import calendar
            year, month = self.date_start.year, self.date_start.month
            self.date_start = self.date_start.replace(day=1)
            last_day = calendar.monthrange(year, month)[1]
            self.date_end = self.date_start.replace(day=last_day)

    def action_generate(self):
        self.ensure_one()
        Sheet = self.env['dcg.timesheet.sheet']
        existing = Sheet.search([
            ('employee_id', '=', self.employee_id.id),
            ('date_start', '=', self.date_start),
            ('date_end', '=', self.date_end),
        ], limit=1)
        if existing:
            raise UserError(_(
                "A sheet already exists for this employee and period: %s"
            ) % existing.name)

        sheet = Sheet.create({
            'employee_id': self.employee_id.id,
            'user_id': self.employee_id.user_id.id or self.env.uid,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'period_type': self.period_type,
        })
        sheet.action_load_lines()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.timesheet.sheet',
            'res_id': sheet.id,
            'view_mode': 'form',
            'target': 'current',
        }
