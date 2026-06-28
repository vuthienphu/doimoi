# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


PROJECT_TYPE_SELECTION = [
    ('implementation', 'Implementation'),
    ('customization', 'Customization'),
    ('support', 'Support'),
    ('training', 'Training'),
    ('consulting', 'Consulting'),
    ('internal', 'Internal'),
]

PROJECT_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('ready', 'Ready for Delivery'),
    ('in_progress', 'In Progress'),
    ('on_hold', 'On Hold'),
    ('uat', 'UAT'),
    ('done', 'Completed'),
    ('closed', 'Closed'),
    ('cancelled', 'Cancelled'),
]

HEALTH_STATUS_SELECTION = [
    ('green', 'Green'),
    ('yellow', 'Yellow'),
    ('red', 'Red'),
]


class DcgProjectDelivery(models.Model):
    _name = 'dcg.project.delivery'
    _description = 'Project Delivery'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Project Name', required=True, tracking=True,
    )
    project_code = fields.Char(
        string='Project Code', index=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True, default=lambda self: self.env.company.currency_id,
    )

    # ============================================================
    # Source
    # ============================================================
    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True,
        ondelete='restrict', index=True, tracking=True,
    )
    lead_id = fields.Many2one('crm.lead', string='Opportunity')
    quotation_id = fields.Many2one('sale.order', string='Quotation')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True, tracking=True, index=True,
    )
    estimate_id = fields.Many2one('dcg.crm.estimate', string='Source Estimate')

    # ============================================================
    # Management
    # ============================================================
    project_manager_id = fields.Many2one(
        'res.users', string='Project Manager', tracking=True, index=True,
    )
    delivery_owner_id = fields.Many2one('res.users', string='Delivery Owner', tracking=True)
    presales_owner_id = fields.Many2one('res.users', string='Presales Owner')
    project_type = fields.Selection(
        selection=PROJECT_TYPE_SELECTION, string='Project Type',
        default='implementation', tracking=True,
    )
    odoo_project_id = fields.Many2one('project.project', string='Odoo Project')

    # ============================================================
    # Timeline
    # ============================================================
    kick_off_date = fields.Date(string='Kick-off Date')
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    actual_end_date = fields.Date(string='Actual End Date')
    warranty_start_date = fields.Date(string='Warranty Start')
    warranty_end_date = fields.Date(string='Warranty End')

    # ============================================================
    # State
    # ============================================================
    state = fields.Selection(
        selection=PROJECT_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True, index=True,
    )

    # ============================================================
    # Finance snapshot
    # ============================================================
    contract_amount_total = fields.Monetary(string='Contract Amount', currency_field='currency_id')
    expected_cost = fields.Monetary(string='Expected Cost', currency_field='currency_id')
    expected_margin = fields.Monetary(string='Expected Margin', currency_field='currency_id')
    planned_effort_hours = fields.Float(
        string='Planned Effort (h)', compute='_compute_effort', store=True,
    )
    actual_effort_hours = fields.Float(string='Actual Effort (h)')

    # ============================================================
    # Progress / health
    # ============================================================
    progress_percent = fields.Float(
        string='Progress (%)', compute='_compute_progress', store=True,
    )
    health_status = fields.Selection(
        selection=HEALTH_STATUS_SELECTION, string='Health',
        compute='_compute_health_status', store=True, tracking=True,
    )
    overall_note = fields.Html(string='Overall Note')

    # ============================================================
    # Content
    # ============================================================
    project_summary = fields.Html(string='Project Summary')
    scope_summary = fields.Html(string='Scope Summary')
    implementation_method = fields.Html(string='Implementation Method')
    assumption_note = fields.Html(string='Assumptions')
    exclusion_note = fields.Html(string='Exclusions')
    risk_summary = fields.Html(string='Risk Summary')
    handover_note = fields.Html(string='Handover Note')

    # ============================================================
    # Relations
    # ============================================================
    scope_ids = fields.One2many('dcg.project.scope', 'project_id', string='Scope / Work Packages')
    milestone_ids = fields.One2many('dcg.project.milestone', 'project_id', string='Milestones')
    member_ids = fields.One2many('dcg.project.member', 'project_id', string='Team Members')
    issue_ids = fields.One2many('dcg.project.issue', 'project_id', string='Issues / Risks')
    change_request_ids = fields.One2many('dcg.project.change.request', 'project_id', string='Change Requests')
    task_ids = fields.One2many('dcg.project.task', 'project_id', string='Tasks')

    scope_count = fields.Integer(compute='_compute_counts')
    milestone_count = fields.Integer(compute='_compute_counts')
    issue_count = fields.Integer(compute='_compute_counts')
    change_request_count = fields.Integer(compute='_compute_counts')
    member_count = fields.Integer(compute='_compute_counts')
    task_count = fields.Integer(compute='_compute_counts')

    # ============================================================
    # Compute
    # ============================================================
    def _compute_counts(self):
        for rec in self:
            rec.scope_count = len(rec.scope_ids)
            rec.milestone_count = len(rec.milestone_ids)
            rec.issue_count = len(rec.issue_ids)
            rec.change_request_count = len(rec.change_request_ids)
            rec.member_count = len(rec.member_ids)
            rec.task_count = len(rec.task_ids)

    @api.depends('scope_ids.planned_hours')
    def _compute_effort(self):
        for rec in self:
            rec.planned_effort_hours = sum(rec.scope_ids.mapped('planned_hours'))

    @api.depends('scope_ids.progress_percent')
    def _compute_progress(self):
        for rec in self:
            scopes = rec.scope_ids.filtered(lambda s: s.state != 'cancelled')
            if scopes:
                rec.progress_percent = sum(scopes.mapped('progress_percent')) / len(scopes)
            else:
                rec.progress_percent = 0.0

    @api.depends('issue_ids.priority', 'issue_ids.state')
    def _compute_health_status(self):
        for rec in self:
            open_issues = rec.issue_ids.filtered(lambda i: i.state in ('open', 'in_progress'))
            if open_issues.filtered(lambda i: i.priority == 'critical'):
                rec.health_status = 'red'
            elif open_issues.filtered(lambda i: i.priority == 'high'):
                rec.health_status = 'yellow'
            else:
                rec.health_status = 'green'

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('project_code', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.project.delivery')
                vals['project_code'] = seq or _('New')
        return super().create(vals_list)

    # ============================================================
    # State actions
    # ============================================================
    def action_mark_ready(self):
        for rec in self:
            if not rec.project_manager_id:
                raise UserError(_("Please assign a Project Manager before marking as ready."))
            rec.write({'state': 'ready'})

    def action_start_project(self):
        for rec in self:
            if rec.state not in ('ready', 'on_hold'):
                raise UserError(_("Project must be ready or on hold to start."))
            rec.write({'state': 'in_progress', 'start_date': rec.start_date or fields.Date.today()})

    def action_set_on_hold(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_("Only in-progress projects can be set on hold."))
            rec.write({'state': 'on_hold'})

    def action_move_to_uat(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_("Project must be in progress to move to UAT."))
            rec.write({'state': 'uat'})

    def action_mark_done(self):
        for rec in self:
            if rec.state not in ('in_progress', 'uat'):
                raise UserError(_("Project must be in progress or UAT to mark as done."))
            rec.write({'state': 'done', 'actual_end_date': rec.actual_end_date or fields.Date.today()})

    def action_close_project(self):
        for rec in self:
            if rec.state != 'done':
                raise UserError(_("Project must be completed before closing."))
            rec.write({'state': 'closed'})

    def action_cancel_project(self):
        for rec in self:
            if rec.state == 'closed':
                raise UserError(_("Closed project cannot be cancelled."))
            rec.write({'state': 'cancelled'})

    # ============================================================
    # Related actions
    # ============================================================
    def action_view_contract(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.contract',
            'res_id': self.contract_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_issue(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Issue'),
            'res_model': 'dcg.project.issue',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_project_id': self.id, 'default_raised_by_id': self.env.uid},
        }

    def action_create_change_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Change Request'),
            'res_model': 'dcg.project.change.request',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_project_id': self.id,
                'default_contract_id': self.contract_id.id,
            },
        }

    def action_view_issues(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Issues / Risks'),
            'res_model': 'dcg.project.issue',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_change_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Change Requests'),
            'res_model': 'dcg.project.change.request',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_milestones(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Milestones'),
            'res_model': 'dcg.project.milestone',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'res_model': 'dcg.project.task',
            'view_mode': 'kanban,list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
