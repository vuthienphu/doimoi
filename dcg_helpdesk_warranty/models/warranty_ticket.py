# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


TICKET_TYPE_SELECTION = [
    ('bug', 'Bug'),
    ('issue', 'Issue'),
    ('question', 'Question'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('change_request', 'Change Request'),
    ('other', 'Other'),
]

TICKET_CATEGORY_SELECTION = [
    ('functional', 'Functional'),
    ('technical', 'Technical'),
    ('database', 'Database'),
    ('integration', 'Integration'),
    ('infrastructure', 'Infrastructure'),
    ('training', 'Training'),
]

SEVERITY_SELECTION = [
    ('critical', 'Critical'),
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
]

PRIORITY_SELECTION = [
    ('highest', 'Highest'),
    ('high', 'High'),
    ('normal', 'Normal'),
    ('low', 'Low'),
]

WARRANTY_RESULT_SELECTION = [
    ('fixed', 'Fixed'),
    ('workaround', 'Workaround'),
    ('guidance', 'Guidance'),
    ('duplicate', 'Duplicate'),
    ('cannot_reproduce', 'Cannot Reproduce'),
    ('rejected', 'Rejected'),
]


class DcgWarrantyTicket(models.Model):
    _name = 'dcg.warranty.ticket'
    _description = 'Warranty Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Ticket No.', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    title = fields.Char(string='Title', required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )

    # ============================================================
    # Customer
    # ============================================================
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True, tracking=True, index=True,
    )
    contact_id = fields.Many2one(
        'res.partner', string='Contact Person',
        domain="['|', ('parent_id', '=', partner_id), ('id', '=', partner_id)]",
    )
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    # ============================================================
    # Project / contract links
    # ============================================================
    project_id = fields.Many2one('dcg.project.delivery', string='Project')
    contract_id = fields.Many2one('dcg.contract', string='Contract')
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Scope',
        domain="[('project_id', '=', project_id)]",
    )

    # ============================================================
    # Classification
    # ============================================================
    ticket_type = fields.Selection(
        selection=TICKET_TYPE_SELECTION, string='Type',
        required=True, default='issue', tracking=True,
    )
    ticket_category = fields.Selection(
        selection=TICKET_CATEGORY_SELECTION, string='Category',
    )
    severity = fields.Selection(
        selection=SEVERITY_SELECTION, string='Severity',
        default='medium', tracking=True,
    )
    priority = fields.Selection(
        selection=PRIORITY_SELECTION, string='Priority',
        default='normal', tracking=True,
    )
    tag_ids = fields.Many2many(
        'dcg.warranty.ticket.tag', string='Tags',
        help='Multi-dimensional classification.',
    )

    # ============================================================
    # Stage (dynamic workflow — kanban)
    # ============================================================
    stage_id = fields.Many2one(
        'dcg.warranty.ticket.stage', string='Stage',
        tracking=True, index=True, copy=False,
        default=lambda self: self._default_stage(),
        group_expand='_read_group_stage_ids',
    )
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked'),
    ], string='Kanban State', default='normal')

    # ============================================================
    # Warranty
    # ============================================================
    warranty_start_date = fields.Date(
        string='Warranty Start', related='contract_id.end_date', store=True,
    )
    warranty_end_date = fields.Date(
        string='Warranty End', related='contract_id.warranty_end_date', store=True,
    )
    is_in_warranty = fields.Boolean(
        string='In Warranty', compute='_compute_is_in_warranty', store=True,
    )

    # ============================================================
    # SLA
    # ============================================================
    sla_id = fields.Many2one('dcg.warranty.sla', string='SLA Policy')
    response_deadline = fields.Datetime(string='Response Deadline')
    resolve_deadline = fields.Datetime(string='Resolve Deadline')
    sla_breached = fields.Boolean(string='SLA Breached', compute='_compute_sla_breached', store=True)

    # ============================================================
    # Assignment
    # ============================================================
    team_id = fields.Many2one('dcg.warranty.team', string='Team', tracking=True)
    owner_id = fields.Many2one('res.users', string='Owner', tracking=True)
    support_engineer_id = fields.Many2one(
        'res.users', string='Engineer', tracking=True,
    )
    reviewer_id = fields.Many2one('res.users', string='Reviewer')

    # ============================================================
    # Dates
    # ============================================================
    assign_date = fields.Datetime(string='Assigned Date')
    response_date = fields.Datetime(string='First Response Date')
    resolve_date = fields.Datetime(string='Resolved Date')
    close_date = fields.Datetime(string='Closed Date')

    # ============================================================
    # Content
    # ============================================================
    summary = fields.Text(string='Summary')
    description = fields.Html(string='Description')
    root_cause = fields.Html(string='Root Cause')
    solution_text = fields.Html(string='Solution')
    customer_feedback = fields.Text(string='Customer Feedback')
    warranty_result = fields.Selection(
        selection=WARRANTY_RESULT_SELECTION, string='Result',
    )

    # Version tracking
    affected_version = fields.Char(string='Affected Version')
    fixed_version = fields.Char(string='Fixed Version')
    commit_url = fields.Char(string='Commit URL')

    # ============================================================
    # Effort
    # ============================================================
    estimated_hours = fields.Float(string='Estimated Hours')
    spent_hours = fields.Float(string='Spent Hours')

    # ============================================================
    # Attachments
    # ============================================================
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_warranty_ticket_attachment_rel',
        'ticket_id', 'attachment_id', string='Attachments',
    )

    # ============================================================
    # Relations
    # ============================================================
    activity_line_ids = fields.One2many(
        'dcg.warranty.activity', 'ticket_id', string='Activity Timeline',
    )
    solution_id = fields.Many2one(
        'dcg.warranty.solution', string='Solution Reference',
    )
    activity_count = fields.Integer(compute='_compute_counts')

    # ============================================================
    # Defaults / helpers
    # ============================================================
    @api.model
    def _default_stage(self):
        return self.env['dcg.warranty.ticket.stage'].search(
            [('is_start', '=', True)], limit=1,
        )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """Show all stages in kanban, not just used ones."""
        return self.env['dcg.warranty.ticket.stage'].search(
            [('active', '=', True)], order='sequence'
        )

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('contract_id.end_date', 'contract_id.warranty_end_date')
    def _compute_is_in_warranty(self):
        today = fields.Date.today()
        for rec in self:
            start = rec.warranty_start_date
            end = rec.warranty_end_date
            rec.is_in_warranty = bool(start and end and start <= today <= end)

    @api.depends('resolve_deadline', 'resolve_date')
    def _compute_sla_breached(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.resolve_deadline:
                resolved = rec.resolve_date or now
                rec.sla_breached = resolved > rec.resolve_deadline
            else:
                rec.sla_breached = False

    def _compute_counts(self):
        for rec in self:
            rec.activity_count = len(rec.activity_line_ids)

    # ============================================================
    # Onchange
    # ============================================================
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.contract_id = self.project_id.contract_id
            self.partner_id = self.project_id.partner_id
            self.scope_id = False

    @api.onchange('severity', 'priority')
    def _onchange_sla_lookup(self):
        """Auto-select SLA policy based on severity + priority."""
        if self.severity:
            domain = [('severity', '=', self.severity)]
            if self.priority:
                domain.append(('priority', '=', self.priority))
            sla = self.env['dcg.warranty.sla'].search(domain, limit=1)
            if sla:
                self.sla_id = sla

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.warranty.ticket')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def write(self, vals):
        # Track stage changes for dates
        if 'stage_id' in vals:
            stage = self.env['dcg.warranty.ticket.stage'].browse(vals['stage_id'])
            if stage.is_done and not self.resolve_date:
                vals['resolve_date'] = fields.Datetime.now()
        if 'support_engineer_id' in vals and vals['support_engineer_id'] and not self.assign_date:
            vals['assign_date'] = fields.Datetime.now()
        return super().write(vals)

    # ============================================================
    # Actions
    # ============================================================
    def action_assign_to_me(self):
        self.write({
            'support_engineer_id': self.env.uid,
            'assign_date': self.assign_date or fields.Datetime.now(),
        })

    def action_mark_response(self):
        self.write({'response_date': fields.Datetime.now()})

    def action_close(self):
        for rec in self:
            stage = self.env['dcg.warranty.ticket.stage'].search(
                [('is_done', '=', True)], limit=1,
            )
            if stage:
                rec.write({
                    'stage_id': stage.id,
                    'close_date': fields.Datetime.now(),
                })
