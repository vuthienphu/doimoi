# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgDocumentVersion(models.Model):
    _name = 'dcg.document.version'
    _description = 'Document Version'
    _order = 'create_date desc'

    document_id = fields.Many2one(
        'dcg.document', string='Document', required=True,
        ondelete='cascade', index=True,
    )
    version_number = fields.Char(string='Version', required=True, default='1.0')
    attachment_id = fields.Many2one(
        'ir.attachment', string='File',
        help='Physical file for this version.',
    )
    file_name = fields.Char(related='attachment_id.name', string='File Name')
    file_size = fields.Integer(related='attachment_id.file_size', string='Size')
    change_log = fields.Text(string='Change Log')
    created_by_id = fields.Many2one(
        'res.users', string='Created By',
        default=lambda self: self.env.user, readonly=True,
    )
    is_current = fields.Boolean(string='Current Version')

    def action_set_current(self):
        """Mark this version as current and unmark others."""
        self.ensure_one()
        self.document_id.version_ids.write({'is_current': False})
        self.write({'is_current': True})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # Auto-set new version as current
            rec.document_id.version_ids.filtered(
                lambda v: v.id != rec.id
            ).write({'is_current': False})
            rec.is_current = True
        return records
