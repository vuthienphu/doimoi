# -*- coding: utf-8 -*-
from odoo import api, fields, models


LINK_MODEL_SELECTION = [
    ('res.partner', 'Customer'),
    ('crm.lead', 'Opportunity'),
    ('dcg.contract', 'Contract'),
    ('dcg.contract.appendix', 'Appendix'),
    ('dcg.project.delivery', 'Project'),
    ('dcg.warranty.ticket', 'Ticket'),
    ('dcg.business.trip', 'Business Trip'),
    ('dcg.project.finance', 'Finance'),
]


class DcgDocumentLink(models.Model):
    _name = 'dcg.document.link'
    _description = 'Document Business Link'
    _order = 'document_id, id'

    document_id = fields.Many2one(
        'dcg.document', string='Document', required=True,
        ondelete='cascade', index=True,
    )
    link_model = fields.Selection(
        selection=LINK_MODEL_SELECTION, string='Object Type', required=True,
    )
    link_res_id = fields.Integer(string='Object ID', required=True)
    link_name = fields.Char(
        string='Object Name', compute='_compute_link_name', store=True,
    )
    note = fields.Char(string='Note')

    @api.depends('link_model', 'link_res_id')
    def _compute_link_name(self):
        for rec in self:
            if rec.link_model and rec.link_res_id:
                obj = self.env[rec.link_model].browse(rec.link_res_id)
                rec.link_name = obj.display_name if obj.exists() else ''
            else:
                rec.link_name = ''
