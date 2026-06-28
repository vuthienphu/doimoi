# -*- coding: utf-8 -*-
from odoo import models


class DcgTicketPriority(models.Model):
    _name = 'dcg.ticket.priority'
    _inherit = 'dcg.master.mixin'
    _description = 'Ticket Priority'
    _order = 'sequence, code, name'

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Ticket Priority code must be unique.',
        ),
    ]
