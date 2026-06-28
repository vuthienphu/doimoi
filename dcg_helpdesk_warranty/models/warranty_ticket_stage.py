# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgWarrantyTicketStage(models.Model):
    _name = 'dcg.warranty.ticket.stage'
    _description = 'Warranty Ticket Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage', required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string='Description')
    fold = fields.Boolean(string='Folded in Kanban')
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color')

    # Workflow flags
    is_start = fields.Boolean(string='Start Stage')
    is_done = fields.Boolean(string='Done Stage')
    is_cancel = fields.Boolean(string='Cancel Stage')
    allow_edit = fields.Boolean(string='Allow Edit', default=True)

    # SLA control
    sla_running = fields.Boolean(string='SLA Running', default=True,
        help='SLA clock ticks while ticket is in this stage.')
    pause_sla = fields.Boolean(string='Pause SLA',
        help='SLA clock pauses (e.g. Waiting Customer).')
    stop_sla = fields.Boolean(string='Stop SLA',
        help='SLA clock stops permanently (e.g. Resolved).')

    # Scope
    team_ids = fields.Many2many(
        'dcg.warranty.team', string='Teams',
        help='Limit this stage to specific teams. Empty = all teams.',
    )
