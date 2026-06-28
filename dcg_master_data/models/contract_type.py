# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgContractType(models.Model):
    _name = 'dcg.contract.type'
    _inherit = 'dcg.master.mixin'
    _description = 'Contract Type'
    _order = 'sequence, code, name'

    description = fields.Text(
        string='Description',
        translate=True,
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Contract Type code must be unique.',
        ),
    ]
