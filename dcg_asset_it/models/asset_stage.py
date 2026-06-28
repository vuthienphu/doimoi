# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgAssetStage(models.Model):
    _name = 'dcg.asset.stage'
    _description = 'Asset Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage', required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded')
    is_start = fields.Boolean(string='Start Stage')
    is_end = fields.Boolean(string='End Stage')
    active = fields.Boolean(default=True)
