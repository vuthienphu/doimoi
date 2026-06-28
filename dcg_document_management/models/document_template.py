# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgDocumentTemplate(models.Model):
    _name = 'dcg.document.template'
    _description = 'Document Template'
    _order = 'sequence, name'

    name = fields.Char(string='Template', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    type_id = fields.Many2one('dcg.document.type', string='Document Type')
    category_id = fields.Many2one('dcg.document.category', string='Category')
    folder_id = fields.Many2one('dcg.document.folder', string='Default Folder')
    tag_ids = fields.Many2many('dcg.document.tag', string='Default Tags')
    attachment_id = fields.Many2one(
        'ir.attachment', string='Template File',
        help='File mẫu dùng làm bản gốc khi tạo document.',
    )
    description = fields.Html(string='Description / Instructions')
    default_content = fields.Html(string='Default Content')
