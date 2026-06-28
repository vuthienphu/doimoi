# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgAssetType(models.Model):
    _name = 'dcg.asset.type'
    _description = 'Asset Type'
    _order = 'sequence, name'

    name = fields.Char(string='Type', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
