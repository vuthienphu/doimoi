# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgContractAppendixType(models.Model):
    _name = 'dcg.contract.appendix.type'
    _inherit = 'dcg.master.mixin'
    _description = 'Contract Appendix Type'
    _order = 'sequence, code, name'

    description = fields.Text(
        string='Description',
        translate=True,
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Contract Appendix Type code must be unique.',
        ),
    ]
