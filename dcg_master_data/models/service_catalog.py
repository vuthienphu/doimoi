# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgServiceCatalog(models.Model):
    _name = 'dcg.service.catalog'
    _description = 'Service Catalog'
    _order = 'sequence, code, name'

    name = fields.Char(
        string='Service Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Service Code',
        index=True,
    )
    service_type = fields.Selection(
        selection=[
            ('implementation', 'Implementation'),
            ('support', 'Support'),
            ('license', 'License'),
            ('consulting', 'Consulting'),
            ('training', 'Training'),
            ('other', 'Other'),
        ],
        string='Service Type',
        required=True,
        default='implementation',
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Internal Note', translate=True)

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Service Catalog code must be unique.',
        ),
    ]
