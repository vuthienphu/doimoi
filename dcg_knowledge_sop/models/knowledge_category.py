# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgKnowledgeCategory(models.Model):
    _name = 'dcg.knowledge.category'
    _description = 'Knowledge Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category', required=True, translate=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color')
    description = fields.Text(string='Description')
    article_count = fields.Integer(compute='_compute_article_count')

    def _compute_article_count(self):
        Article = self.env['dcg.knowledge.article']
        for rec in self:
            rec.article_count = Article.search_count(
                [('category_id', '=', rec.id)]
            ) if rec.id else 0
