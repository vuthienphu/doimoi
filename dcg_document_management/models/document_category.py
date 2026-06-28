# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgDocumentCategory(models.Model):
    _name = 'dcg.document.category'
    _description = 'Document Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
