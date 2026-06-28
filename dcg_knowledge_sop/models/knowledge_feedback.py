# -*- coding: utf-8 -*-
from odoo import fields, models


RATING_SELECTION = [
    ('1', '1 - Poor'),
    ('2', '2 - Fair'),
    ('3', '3 - Good'),
    ('4', '4 - Very Good'),
    ('5', '5 - Excellent'),
]


class DcgKnowledgeFeedback(models.Model):
    _name = 'dcg.knowledge.feedback'
    _description = 'Knowledge Article Feedback'
    _order = 'create_date desc'

    article_id = fields.Many2one(
        'dcg.knowledge.article', string='Article', required=True,
        ondelete='cascade', index=True,
    )
    user_id = fields.Many2one(
        'res.users', string='User', required=True,
        default=lambda self: self.env.user,
    )
    rating = fields.Float(string='Rating (1-5)')
    is_helpful = fields.Boolean(string='Helpful')
    comment = fields.Text(string='Comment')
