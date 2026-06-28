# -*- coding: utf-8 -*-
from odoo import models


class DcgCustomerIndustry(models.Model):
    _name = 'dcg.customer.industry'
    _inherit = 'dcg.master.mixin'
    _description = 'Customer Industry'
    _order = 'sequence, code, name'

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Customer Industry code must be unique.',
        ),
    ]
