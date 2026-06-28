# -*- coding: utf-8 -*-
from odoo import models


class DcgCustomerSource(models.Model):
    _name = 'dcg.customer.source'
    _inherit = 'dcg.master.mixin'
    _description = 'Customer Source'
    _order = 'sequence, code, name'

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Customer Source code must be unique.',
        ),
    ]
