# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgDocumentFolder(models.Model):
    _name = 'dcg.document.folder'
    _description = 'Document Folder'
    _parent_name = 'parent_id'
    _order = 'sequence, complete_name'
    _rec_name = 'complete_name'

    name = fields.Char(string='Name', required=True)
    complete_name = fields.Char(
        string='Full Path', compute='_compute_complete_name', store=True, recursive=True,
    )
    parent_id = fields.Many2one(
        'dcg.document.folder', string='Parent Folder', ondelete='cascade', index=True,
    )
    child_ids = fields.One2many('dcg.document.folder', 'parent_id', string='Sub-folders')
    sequence = fields.Integer(default=10)
    manager_id = fields.Many2one('res.users', string='Manager')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    document_count = fields.Integer(compute='_compute_document_count')

    def _compute_complete_name(self):
        for folder in self:
            if folder.parent_id:
                folder.complete_name = '%s / %s' % (folder.parent_id.complete_name, folder.name)
            else:
                folder.complete_name = folder.name

    def _compute_document_count(self):
        Doc = self.env['dcg.document']
        for folder in self:
            folder.document_count = Doc.search_count(
                [('folder_id', '=', folder.id)]
            ) if folder.id else 0
