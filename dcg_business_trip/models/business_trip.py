# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


TRIP_TYPE_SELECTION = [
    ('project_onsite', 'Project Onsite'),
    ('customer_meeting', 'Customer Meeting'),
    ('survey', 'Survey'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('internal', 'Internal'),
    ('other', 'Other'),
]

TRIP_PURPOSE_SELECTION = [
    ('kickoff', 'Kickoff'),
    ('requirement', 'Requirement Survey'),
    ('implementation', 'Implementation'),
    ('uat', 'UAT'),
    ('golive', 'Go-live'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('warranty', 'Warranty'),
    ('meeting', 'Meeting'),
    ('other', 'Other'),
]

TRIP_WORK_TYPE_SELECTION = [
    ('project_delivery', 'Project Delivery'),
    ('presales', 'Presales'),
    ('support', 'Support'),
    ('internal', 'Internal'),
    ('other', 'Other'),
]

TRIP_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('waiting_approval', 'Waiting Approval'),
    ('approved', 'Approved'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
]


class DcgBusinessTrip(models.Model):
    _name = 'dcg.business.trip'
    _description = 'Business Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'dcg.approval.mixin']
    _order = 'request_date desc, id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Trip Code', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    title = fields.Char(string='Title', required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True, default=lambda self: self.env.company.currency_id,
    )
    active = fields.Boolean(default=True)

    # ============================================================
    # Requester / owner
    # ============================================================
    requester_id = fields.Many2one(
        'res.users', string='Requester', required=True,
        default=lambda self: self.env.user, tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        default=lambda self: self.env.user.employee_id, tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department', string='Department',
        related='employee_id.department_id', store=True,
    )
    manager_id = fields.Many2one(
        'res.users', string='Manager',
        related='employee_id.parent_id.user_id', store=True,
    )

    # ============================================================
    # Business links
    # ============================================================
    partner_id = fields.Many2one('res.partner', string='Customer / Partner')
    project_id = fields.Many2one('dcg.project.delivery', string='Project')
    contract_id = fields.Many2one('dcg.contract', string='Contract')
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Scope',
        domain="[('project_id', '=', project_id)]",
    )
    milestone_id = fields.Many2one(
        'dcg.project.milestone', string='Milestone',
        domain="[('project_id', '=', project_id)]",
    )
    finance_id = fields.Many2one('dcg.project.finance', string='Finance Record')

    # ============================================================
    # Classification
    # ============================================================
    trip_type = fields.Selection(
        selection=TRIP_TYPE_SELECTION, string='Trip Type',
        default='project_onsite', tracking=True,
    )
    trip_purpose = fields.Selection(
        selection=TRIP_PURPOSE_SELECTION, string='Purpose',
        default='implementation',
    )
    work_type = fields.Selection(
        selection=TRIP_WORK_TYPE_SELECTION, string='Work Type',
        default='project_delivery',
    )
    is_billable = fields.Boolean(string='Billable')
    is_onsite = fields.Boolean(string='Onsite', default=True)

    # ============================================================
    # Schedule
    # ============================================================
    request_date = fields.Date(
        string='Request Date', required=True,
        default=fields.Date.context_today, tracking=True,
    )
    start_datetime = fields.Datetime(string='Departure', required=True)
    end_datetime = fields.Datetime(string='Return', required=True)
    total_days = fields.Float(
        string='Total Days', compute='_compute_total_days', store=True,
    )
    departure_place = fields.Char(string='From')
    destination_place = fields.Char(string='Destination', required=True)
    destination_address = fields.Text(string='Destination Address')
    note_schedule = fields.Text(string='Schedule Note')

    # ============================================================
    # Content
    # ============================================================
    objective = fields.Html(string='Objective')
    agenda = fields.Html(string='Agenda')
    expected_result = fields.Html(string='Expected Result')
    internal_note = fields.Text(string='Internal Note')

    # ============================================================
    # State
    # ============================================================
    state = fields.Selection(
        selection=TRIP_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True, index=True,
    )
    cancel_reason = fields.Text(string='Cancel Reason')

    # ============================================================
    # Cost summary (compute from expense lines)
    # ============================================================
    estimated_cost = fields.Monetary(
        string='Estimated Cost', currency_field='currency_id',
        compute='_compute_costs', store=True,
    )
    actual_cost = fields.Monetary(
        string='Actual Cost', currency_field='currency_id',
        compute='_compute_costs', store=True,
    )
    cost_variance = fields.Monetary(
        string='Cost Variance', currency_field='currency_id',
        compute='_compute_costs', store=True,
    )

    # ============================================================
    # Relations
    # ============================================================
    member_ids = fields.One2many(
        'dcg.business.trip.member', 'trip_id', string='Members',
    )
    expense_ids = fields.One2many(
        'dcg.business.trip.expense', 'trip_id', string='Expenses',
    )
    member_count = fields.Integer(compute='_compute_counts')
    expense_count = fields.Integer(compute='_compute_counts')

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('start_datetime', 'end_datetime')
    def _compute_total_days(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime and rec.end_datetime > rec.start_datetime:
                delta = rec.end_datetime - rec.start_datetime
                rec.total_days = delta.total_seconds() / 86400.0
            else:
                rec.total_days = 0.0

    @api.depends('expense_ids.amount', 'expense_ids.source_type')
    def _compute_costs(self):
        for rec in self:
            estimated = sum(
                e.amount for e in rec.expense_ids if e.source_type == 'estimated'
            )
            actual = sum(
                e.amount for e in rec.expense_ids if e.source_type == 'actual'
            )
            rec.estimated_cost = estimated
            rec.actual_cost = actual
            rec.cost_variance = actual - estimated

    def _compute_counts(self):
        for rec in self:
            rec.member_count = len(rec.member_ids)
            rec.expense_count = len(rec.expense_ids)

    # ============================================================
    # Onchange
    # ============================================================
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.contract_id = self.project_id.contract_id
            self.partner_id = self.project_id.partner_id
            self.finance_id = self.project_id.finance_id
            self.scope_id = False
            self.milestone_id = False

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.business.trip')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    # ============================================================
    # Approval mixin overrides
    # ============================================================
    def _get_approval_type(self):
        return 'business_trip_approval'

    def _get_approval_amount(self):
        return self.estimated_cost or 0.0

    def _validate_before_submit_approval(self):
        self.ensure_one()
        if not self.member_ids:
            raise UserError(_("Please add at least one member before submitting."))
        if not self.start_datetime or not self.end_datetime:
            raise UserError(_("Please set departure and return dates."))
        return True

    def _approval_approved_callback(self, request):
        self.ensure_one()
        super()._approval_approved_callback(request)
        self.write({'state': 'approved'})

    def _approval_rejected_callback(self, request):
        self.ensure_one()
        super()._approval_rejected_callback(request)
        self.write({'state': 'draft'})

    # ============================================================
    # State actions
    # ============================================================
    def action_submit_approval(self):
        for rec in self:
            rec.state = 'waiting_approval'
        return super().action_submit_approval()

    def action_start_trip(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Trip must be approved before starting."))
            rec.write({'state': 'in_progress'})

    def action_mark_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_("Trip must be in progress to mark as done."))
            rec.write({'state': 'done'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("Cannot cancel a completed trip."))
            rec.write({'state': 'cancelled'})

    # ============================================================
    # Finance sync (spec mục 48-51)
    # ============================================================
    def action_sync_to_finance(self):
        """Sync actual expenses → project finance cost lines."""
        self.ensure_one()
        if not self.finance_id:
            raise UserError(_(
                "This trip is not linked to a project finance record. "
                "Please set a project with an active finance record."
            ))
        self._sync_trip_expenses_to_finance()
        return True

    def _sync_trip_expenses_to_finance(self):
        """Idempotent sync: each actual expense → 1 finance cost line."""
        self.ensure_one()
        CostLine = self.env['dcg.project.finance.cost.line']
        for exp in self.expense_ids.filtered(lambda e: e.source_type == 'actual'):
            vals = {
                'finance_id': self.finance_id.id,
                'project_id': self.project_id.id if self.project_id else False,
                'contract_id': self.contract_id.id if self.contract_id else False,
                'scope_id': self.scope_id.id if self.scope_id else False,
                'cost_type': 'travel',
                'source_type': 'trip',
                'name': '%s - %s' % (self.name, exp.name),
                'cost_date': exp.expense_date or self.request_date,
                'amount': exp.amount,
                'currency_id': self.currency_id.id,
                'employee_id': exp.member_id.employee_id.id if exp.member_id else (
                    self.employee_id.id if self.employee_id else False
                ),
            }
            if exp.finance_cost_line_id:
                exp.finance_cost_line_id.write(vals)
            else:
                cost_line = CostLine.create(vals)
                exp.write({
                    'finance_cost_line_id': cost_line.id,
                    'finance_synced': True,
                })
