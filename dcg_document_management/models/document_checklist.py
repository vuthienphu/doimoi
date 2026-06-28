# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgDocumentChecklist(models.Model):
    _name = 'dcg.document.checklist'
    _description = 'Document Checklist'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Required Document', required=True)
    category_id = fields.Many2one('dcg.document.category', string='Category')
    type_id = fields.Many2one('dcg.document.type', string='Type')
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    document_id = fields.Many2one(
        'dcg.document', string='Linked Document',
        help='Document that fulfills this checklist item.',
    )
    is_fulfilled = fields.Boolean(
        string='Fulfilled', compute='_compute_is_fulfilled', store=True,
    )
    note = fields.Text(string='Note')

    @api.depends('document_id', 'document_id.state')
    def _compute_is_fulfilled(self):
        for rec in self:
            rec.is_fulfilled = bool(
                rec.document_id and rec.document_id.state in ('approved', 'published')
            )
