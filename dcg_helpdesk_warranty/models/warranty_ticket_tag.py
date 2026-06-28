# -*- coding: utf-8 -*-
from odoo import fields, models


TAG_GROUP_SELECTION = [
    ('module', 'Module'),
    ('issue', 'Issue Type'),
    ('technology', 'Technology'),
    ('business', 'Business'),
    ('other', 'Other'),
]


class DcgWarrantyTicketTag(models.Model):
    _name = 'dcg.warranty.ticket.tag'
    _description = 'Warranty Ticket Tag'
    _order = 'group, sequence, name'

    name = fields.Char(string='Tag', required=True, translate=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    group = fields.Selection(
        selection=TAG_GROUP_SELECTION, string='Group', default='other',
    )
