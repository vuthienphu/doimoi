# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DcgTicketSeverity(models.Model):
    _name = 'dcg.ticket.severity'
    _description = 'Ticket Severity'
    _order = 'sequence, code, name'

    name = fields.Char(
        string='Severity',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        index=True,
    )
    sequence = fields.Integer(default=10)
    response_hours_default = fields.Float(
        string='Default Response Hours',
        help='Default SLA response time in hours.',
    )
    resolution_hours_default = fields.Float(
        string='Default Resolution Hours',
        help='Default SLA resolution time in hours.',
    )
    active = fields.Boolean(default=True)
    note = fields.Text(string='Internal Note', translate=True)

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Ticket Severity code must be unique.',
        ),
    ]

    @api.constrains('response_hours_default', 'resolution_hours_default')
    def _check_hours_positive(self):
        for rec in self:
            if rec.response_hours_default < 0:
                raise ValidationError(_("Default response hours must be greater than or equal to 0."))
            if rec.resolution_hours_default < 0:
                raise ValidationError(_("Default resolution hours must be greater than or equal to 0."))
