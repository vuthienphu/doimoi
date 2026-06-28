# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


DOCUMENT_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('review', 'In Review'),
    ('approved', 'Approved'),
    ('published', 'Published'),
    ('archived', 'Archived'),
    ('cancelled', 'Cancelled'),
]


class DcgDocument(models.Model):
    _name = 'dcg.document'
    _description = 'Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Document Name', required=True, tracking=True)
    code = fields.Char(
        string='Document Code', copy=False,
        default=lambda self: _('New'),
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    owner_id = fields.Many2one(
        'res.users', string='Owner',
        default=lambda self: self.env.user, tracking=True,
    )

    # Classification
    folder_id = fields.Many2one('dcg.document.folder', string='Folder', tracking=True)
    type_id = fields.Many2one('dcg.document.type', string='Type', tracking=True)
    category_id = fields.Many2one('dcg.document.category', string='Category')
    tag_ids = fields.Many2many(
        'dcg.document.tag', 'dcg_document_tag_rel',
        'document_id', 'tag_id', string='Tags',
    )
    template_id = fields.Many2one('dcg.document.template', string='From Template')

    # Direct business links (quick access — spec mục 10)
    partner_id = fields.Many2one('res.partner', string='Customer')
    project_id = fields.Many2one('dcg.project.delivery', string='Project')
    contract_id = fields.Many2one('dcg.contract', string='Contract')

    # State
    state = fields.Selection(
        selection=DOCUMENT_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True, index=True,
    )
    description = fields.Html(string='Description')
    content = fields.Html(string='Content')

    # Current file (shortcut to latest version attachment)
    current_attachment_id = fields.Many2one(
        'ir.attachment', string='Current File',
        compute='_compute_current_attachment', store=True,
    )
    current_version = fields.Char(
        string='Current Version',
        compute='_compute_current_attachment', store=True,
    )

    # Relations
    version_ids = fields.One2many('dcg.document.version', 'document_id', string='Versions')
    review_ids = fields.One2many('dcg.document.review', 'document_id', string='Reviews')
    link_ids = fields.One2many('dcg.document.link', 'document_id', string='Business Links')
    version_count = fields.Integer(compute='_compute_counts')
    review_count = fields.Integer(compute='_compute_counts')
    link_count = fields.Integer(compute='_compute_counts')

    @api.depends('version_ids', 'version_ids.is_current', 'version_ids.attachment_id')
    def _compute_current_attachment(self):
        for doc in self:
            current = doc.version_ids.filtered('is_current')[:1]
            doc.current_attachment_id = current.attachment_id if current else False
            doc.current_version = current.version_number if current else ''

    def _compute_counts(self):
        for doc in self:
            doc.version_count = len(doc.version_ids)
            doc.review_count = len(doc.review_ids)
            doc.link_count = len(doc.link_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.document')
                vals['code'] = seq or _('New')
        return super().create(vals_list)

    # State actions
    def action_submit_review(self):
        for doc in self:
            if doc.type_id and doc.type_id.requires_version and not doc.version_ids:
                raise UserError(_("Please upload at least one version before submitting for review."))
            doc.write({'state': 'review'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_publish(self):
        self.write({'state': 'published'})

    def action_archive_doc(self):
        self.write({'state': 'archived'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    # Template apply
    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            tpl = self.template_id
            self.type_id = tpl.type_id
            self.category_id = tpl.category_id
            self.folder_id = tpl.folder_id
            self.tag_ids = tpl.tag_ids
            if tpl.default_content:
                self.content = tpl.default_content
