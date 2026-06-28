# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgAcceptanceType(models.Model):
    _name = 'dcg.acceptance.type'
    _inherit = 'dcg.master.mixin'
    _description = 'Acceptance Type'
    _order = 'sequence, code, name'

    description = fields.Text(
        string='Description',
        translate=True,
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Acceptance Type code must be unique.',
        ),
    ]
