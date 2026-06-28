# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgDocumentTag(models.Model):
    _name = 'dcg.document.tag'
    _description = 'Document Tag'
    _order = 'name'

    name = fields.Char(string='Tag', required=True, translate=True)
    color = fields.Integer(string='Color')
    description = fields.Text(string='Description')
