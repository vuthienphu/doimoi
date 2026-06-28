# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


ARTICLE_TYPE_SELECTION = [
    ('sop', 'SOP'),
    ('faq', 'FAQ'),
    ('best_practice', 'Best Practice'),
    ('known_issue', 'Known Issue'),
    ('coding_standard', 'Coding Standard'),
    ('guide', 'Guide'),
    ('checklist', 'Checklist'),
    ('other', 'Other'),
]

ARTICLE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('review', 'In Review'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]

ARTICLE_AUDIENCE_SELECTION = [
    ('all', 'All Employees'),
    ('delivery', 'Delivery Team'),
    ('support', 'Support Team'),
    ('management', 'Management'),
    ('customer', 'Customer Facing'),
]


class DcgKnowledgeArticle(models.Model):
    _name = 'dcg.knowledge.article'
    _description = 'Knowledge Article'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, write_date desc'
    _rec_name = 'title'

    # ---- Identification ----
    title = fields.Char(string='Title', required=True, tracking=True)
    code = fields.Char(
        string='Article Code', copy=False,
        default=lambda self: _('New'),
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )

    # ---- Classification ----
    article_type = fields.Selection(
        selection=ARTICLE_TYPE_SELECTION, string='Type',
        required=True, default='guide', tracking=True,
    )
    category_id = fields.Many2one(
        'dcg.knowledge.category', string='Category', tracking=True,
    )
    tag_ids = fields.Many2many(
        'dcg.knowledge.tag', 'dcg_knowledge_article_tag_rel',
        'article_id', 'tag_id', string='Tags',
    )
    audience = fields.Selection(
        selection=ARTICLE_AUDIENCE_SELECTION, string='Audience',
        default='all',
    )

    # ---- Content ----
    summary = fields.Text(string='Summary')
    content = fields.Html(string='Content', sanitize_style=True)
    # FAQ specific
    question = fields.Text(string='Question')
    answer = fields.Html(string='Answer')
    # Known Issue specific
    problem = fields.Html(string='Problem')
    solution = fields.Html(string='Solution')
    root_cause = fields.Html(string='Root Cause')

    # ---- Lifecycle ----
    state = fields.Selection(
        selection=ARTICLE_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True,
    )
    author_id = fields.Many2one(
        'res.users', string='Author',
        default=lambda self: self.env.user, tracking=True,
    )
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    published_date = fields.Date(string='Published Date')
    expiry_date = fields.Date(string='Expiry Date')
    is_expired = fields.Boolean(compute='_compute_is_expired', store=True)

    # ---- Metrics ----
    view_count = fields.Integer(string='Views', default=0)
    like_count = fields.Integer(string='Likes', default=0)
    is_pinned = fields.Boolean(string='Pinned')
    is_featured = fields.Boolean(string='Featured')

    # ---- Links ----
    project_id = fields.Many2one('dcg.project.delivery', string='Project')
    ticket_id = fields.Many2one('dcg.warranty.ticket', string='Ticket')
    module_name = fields.Char(string='Module')
    keyword = fields.Char(string='Keywords', help='Comma-separated for search.')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_knowledge_article_attach_rel',
        'article_id', 'attachment_id', string='Attachments',
    )

    # ---- Revisions ----
    revision_ids = fields.One2many(
        'dcg.knowledge.revision', 'article_id', string='Revisions',
    )
    current_version = fields.Char(string='Version', default='1.0')

    # ---- Feedback ----
    feedback_ids = fields.One2many(
        'dcg.knowledge.feedback', 'article_id', string='Feedback',
    )
    avg_rating = fields.Float(
        string='Avg Rating', compute='_compute_avg_rating', store=True,
    )

    # ---- Compute ----
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = bool(rec.expiry_date and rec.expiry_date < today)

    @api.depends('feedback_ids.rating')
    def _compute_avg_rating(self):
        for rec in self:
            ratings = rec.feedback_ids.mapped('rating')
            valid = [r for r in ratings if r > 0]
            rec.avg_rating = sum(valid) / len(valid) if valid else 0

    # ---- ORM ----
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.knowledge.article')
                vals['code'] = seq or _('New')
        return super().create(vals_list)

    # ---- State actions ----
    def action_submit_review(self):
        self.write({'state': 'review'})

    def action_publish(self):
        self.write({
            'state': 'published',
            'published_date': fields.Date.today(),
        })

    def action_archive_article(self):
        self.write({'state': 'archived'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_increment_view(self):
        """Called when user opens article."""
        self.sudo().write({'view_count': self.view_count + 1})

    def action_like(self):
        self.sudo().write({'like_count': self.like_count + 1})

    def action_create_revision(self):
        """Snapshot current content as a revision."""
        self.ensure_one()
        self.env['dcg.knowledge.revision'].create({
            'article_id': self.id,
            'version': self.current_version,
            'content_snapshot': self.content,
            'change_note': '',
        })
