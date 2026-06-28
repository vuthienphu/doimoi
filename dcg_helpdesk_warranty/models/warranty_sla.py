# -*- coding: utf-8 -*-
from odoo import fields, models


SEVERITY_SELECTION = [
    ('critical', 'Critical'),
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
]

PRIORITY_SELECTION = [
    ('highest', 'Highest'),
    ('high', 'High'),
    ('normal', 'Normal'),
    ('low', 'Low'),
]


class DcgWarrantySla(models.Model):
    _name = 'dcg.warranty.sla'
    _description = 'Warranty SLA Policy'
    _order = 'sequence, id'

    name = fields.Char(string='SLA Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    severity = fields.Selection(
        selection=SEVERITY_SELECTION, string='Severity',
    )
    priority = fields.Selection(
        selection=PRIORITY_SELECTION, string='Priority',
    )
    response_hours = fields.Float(
        string='Response Time (h)',
        help='Maximum hours to first response.',
    )
    resolve_hours = fields.Float(
        string='Resolve Time (h)',
        help='Maximum hours to resolve.',
    )
    description = fields.Text(string='Description')
    team_id = fields.Many2one('dcg.warranty.team', string='Team')
