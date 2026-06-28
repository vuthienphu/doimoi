# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgDocumentType(models.Model):
    _name = 'dcg.document.type'
    _description = 'Document Type'
    _order = 'sequence, name'

    name = fields.Char(string='Type', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    requires_approval = fields.Boolean(
        string='Requires Approval',
        help='Documents of this type must go through review/approval.',
    )
    requires_version = fields.Boolean(
        string='Requires Version', default=True,
        help='Version tracking is mandatory.',
    )
    portal_visible = fields.Boolean(
        string='Portal Visible',
        help='Customers can view on portal.',
    )
    retention_days = fields.Integer(
        string='Retention (days)',
        help='Default archiving period. 0 = unlimited.',
    )
