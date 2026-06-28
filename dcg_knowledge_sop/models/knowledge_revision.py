# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgKnowledgeRevision(models.Model):
    _name = 'dcg.knowledge.revision'
    _description = 'Knowledge Article Revision'
    _order = 'create_date desc'

    article_id = fields.Many2one(
        'dcg.knowledge.article', string='Article', required=True,
        ondelete='cascade', index=True,
    )
    version = fields.Char(string='Version', required=True)
    content_snapshot = fields.Html(string='Content Snapshot')
    change_note = fields.Text(string='Change Note')
    revised_by_id = fields.Many2one(
        'res.users', string='Revised By',
        default=lambda self: self.env.user, readonly=True,
    )
