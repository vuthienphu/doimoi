# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgAssetLocation(models.Model):
    _name = 'dcg.asset.location'
    _description = 'Asset Location'
    _order = 'name'

    name = fields.Char(string='Location', required=True)
    code = fields.Char(string='Code')
    address = fields.Text(string='Address')
    active = fields.Boolean(default=True)
