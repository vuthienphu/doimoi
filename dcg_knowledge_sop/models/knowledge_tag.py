# -*- coding: utf-8 -*-
from odoo import fields, models


TAG_GROUP_SELECTION = [
    ('module', 'Module'),
    ('technology', 'Technology'),
    ('process', 'Process'),
    ('domain', 'Domain'),
    ('other', 'Other'),
]


class DcgKnowledgeTag(models.Model):
    _name = 'dcg.knowledge.tag'
    _description = 'Knowledge Tag'
    _order = 'group, name'

    name = fields.Char(string='Tag', required=True, translate=True)
    group = fields.Selection(
        selection=TAG_GROUP_SELECTION, string='Group', default='other',
    )
    color = fields.Integer(string='Color')
    active = fields.Boolean(default=True)
