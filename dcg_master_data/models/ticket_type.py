# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgTicketType(models.Model):
    _name = 'dcg.ticket.type'
    _inherit = 'dcg.master.mixin'
    _description = 'Ticket Type'
    _order = 'sequence, code, name'

    description = fields.Text(
        string='Description',
        translate=True,
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Ticket Type code must be unique.',
        ),
    ]
