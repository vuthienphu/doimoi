# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgAssetCategory(models.Model):
    _name = 'dcg.asset.category'
    _description = 'Asset Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
