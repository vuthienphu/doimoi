# -*- coding: utf-8 -*-
from odoo import fields, models


REVIEW_STATUS_SELECTION = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('comment', 'Comment Only'),
]


class DcgDocumentReview(models.Model):
    _name = 'dcg.document.review'
    _description = 'Document Review'
    _order = 'create_date desc'

    document_id = fields.Many2one(
        'dcg.document', string='Document', required=True,
        ondelete='cascade', index=True,
    )
    reviewer_id = fields.Many2one(
        'res.users', string='Reviewer', required=True,
        default=lambda self: self.env.user,
    )
    review_date = fields.Datetime(
        string='Review Date', default=fields.Datetime.now,
    )
    status = fields.Selection(
        selection=REVIEW_STATUS_SELECTION, string='Status',
        required=True, default='pending',
    )
    version_id = fields.Many2one(
        'dcg.document.version', string='Version Reviewed',
    )
    comment = fields.Html(string='Comment')
