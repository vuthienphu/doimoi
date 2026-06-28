# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DcgSlaPolicy(models.Model):
    _name = 'dcg.sla.policy'
    _description = 'SLA Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code, name'

    name = fields.Char(
        string='Policy Name',
        required=True,
        tracking=True,
        translate=True,
    )
    code = fields.Char(
        string='Policy Code',
        index=True,
        tracking=True,
    )
    ticket_type_id = fields.Many2one(
        'dcg.ticket.type',
        string='Ticket Type',
        ondelete='restrict',
    )
    severity_id = fields.Many2one(
        'dcg.ticket.severity',
        string='Severity',
        ondelete='restrict',
    )
    response_hours = fields.Float(
        string='Response Hours',
        required=True,
        tracking=True,
        help='Maximum number of working hours to first respond to a ticket.',
    )
    resolution_hours = fields.Float(
        string='Resolution Hours',
        required=True,
        tracking=True,
        help='Maximum number of working hours to fully resolve a ticket.',
    )
    working_calendar_id = fields.Many2one(
        'resource.calendar',
        string='Working Calendar',
        help='Working calendar used to compute SLA deadlines.',
    )
    active = fields.Boolean(default=True, tracking=True)
    note = fields.Text(string='Internal Note', translate=True)

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'SLA Policy code must be unique.',
        ),
    ]

    @api.constrains('response_hours', 'resolution_hours')
    def _check_sla_hours(self):
        for rec in self:
            if rec.response_hours <= 0:
                raise ValidationError(_("SLA response hours must be greater than 0."))
            if rec.resolution_hours <= 0:
                raise ValidationError(_("SLA resolution hours must be greater than 0."))
            if rec.resolution_hours < rec.response_hours:
                raise ValidationError(_(
                    "SLA resolution hours must be greater than or equal to response hours."
                ))
