# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


COMMERCIAL_STATUS_SELECTION = [
    ('draft', 'Draft'),
    ('qualification', 'Qualification'),
    ('surveying', 'Surveying'),
    ('estimating', 'Estimating'),
    ('waiting_approval', 'Waiting Approval'),
    ('quoted', 'Quoted'),
    ('won', 'Won'),
    ('lost', 'Lost'),
]


class CrmLead(models.Model):
    """Lead/Opportunity mở rộng — trung tâm điều phối presales.

    Approval (phase 1) bám vào lead, dùng dcg.approval.mixin với approval_type
    'deal_approval'. Estimate/requirement/scope/cost không tự approval riêng.
    """
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'dcg.approval.mixin']

    # ============================================================
    # Identification & ownership
    # ============================================================
    opportunity_code = fields.Char(string='Opportunity Code', copy=False, index=True)
    account_manager_id = fields.Many2one(
        'res.users',
        string='Account Manager',
        tracking=True,
    )
    presales_owner_id = fields.Many2one(
        'res.users',
        string='Presales Owner',
        tracking=True,
    )
    presales_team_member_ids = fields.Many2many(
        'res.users',
        'crm_lead_presales_team_rel',
        'lead_id',
        'user_id',
        string='Presales Team',
    )
    lead_source_id = fields.Many2one(
        'dcg.customer.source',
        string='Lead Source',
    )
    industry_id = fields.Many2one(
        'dcg.customer.industry',
        string='DCG Industry',
        help='DCG-specific industry classification snapshot for this opportunity.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # ============================================================
    # Business discovery
    # ============================================================
    customer_need_summary = fields.Html(string='Customer Need Summary')
    pain_point = fields.Html(string='Pain Point')
    business_goal = fields.Html(string='Business Goal')
    current_system = fields.Html(string='Current System')
    competitor_info = fields.Text(string='Competitor Info')
    risk_note = fields.Text(string='Risk Note')
    decision_deadline = fields.Date(string='Decision Deadline')
    expected_go_live_date = fields.Date(string='Expected Go-Live Date')

    # ============================================================
    # Presales / scope summary (synced from estimate, see crm_estimate.py)
    # ============================================================
    solution_scope_summary = fields.Html(string='Solution Scope Summary')
    estimated_ba_hours = fields.Float(string='BA Hours')
    estimated_dev_hours = fields.Float(string='Dev Hours')
    estimated_test_hours = fields.Float(string='Test Hours')
    estimated_pm_hours = fields.Float(string='PM Hours')
    estimated_support_hours = fields.Float(string='Support Hours')
    estimated_timeline_days = fields.Integer(string='Timeline (days)')
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id')
    estimated_revenue = fields.Monetary(string='Estimated Revenue', currency_field='currency_id')
    estimated_margin = fields.Monetary(
        string='Estimated Margin', currency_field='currency_id', compute='_compute_estimated_margin', store=True
    )
    estimated_margin_rate = fields.Float(
        string='Margin Rate (%)', compute='_compute_estimated_margin', store=True
    )
    presales_cost_amount = fields.Monetary(
        string='Presales Cost Total', currency_field='currency_id', compute='_compute_presales_cost_amount'
    )

    # ============================================================
    # Approval / commercial decision
    # ============================================================
    deal_approval_required = fields.Boolean(string='Approval Required')
    deal_submit_note = fields.Text(string='Approval Submission Note')
    commercial_status = fields.Selection(
        selection=COMMERCIAL_STATUS_SELECTION,
        string='Commercial Status',
        default='draft',
        tracking=True,
        index=True,
        help='Presales-specific status, tracked in parallel with the CRM pipeline stage.',
    )

    # ============================================================
    # Statistics / links
    # ============================================================
    requirement_ids = fields.One2many(
        'dcg.crm.requirement', 'lead_id', string='Requirement Surveys'
    )
    solution_scope_ids = fields.One2many(
        'dcg.crm.solution.scope', 'lead_id', string='Solution Scope'
    )
    estimate_ids = fields.One2many(
        'dcg.crm.estimate', 'lead_id', string='Estimates'
    )
    presales_cost_ids = fields.One2many(
        'dcg.crm.presales.cost', 'lead_id', string='Presales Costs'
    )

    requirement_count = fields.Integer(compute='_compute_presales_counts')
    solution_scope_count = fields.Integer(compute='_compute_presales_counts')
    estimate_count = fields.Integer(compute='_compute_presales_counts')
    presales_cost_count = fields.Integer(compute='_compute_presales_counts')
    quotation_count = fields.Integer(compute='_compute_quotation_count')

    latest_estimate_id = fields.Many2one(
        'dcg.crm.estimate', string='Latest Estimate', copy=False, readonly=True
    )
    approved_estimate_id = fields.Many2one(
        'dcg.crm.estimate', string='Approved Estimate', copy=False, readonly=True
    )

    # ============================================================
    # Quotation / handover
    # ============================================================
    quotation_id = fields.Many2one(
        'sale.order', string='Primary Quotation', copy=False, readonly=True
    )
    quotation_ready = fields.Boolean(
        string='Ready for Quotation', compute='_compute_quotation_ready'
    )
    handover_note = fields.Html(string='Handover Note')

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('estimated_revenue', 'estimated_cost')
    def _compute_estimated_margin(self):
        for rec in self:
            rec.estimated_margin = (rec.estimated_revenue or 0.0) - (rec.estimated_cost or 0.0)
            if rec.estimated_revenue:
                rec.estimated_margin_rate = (rec.estimated_margin / rec.estimated_revenue) * 100.0
            else:
                rec.estimated_margin_rate = 0.0

    def _compute_presales_cost_amount(self):
        for rec in self:
            costs = rec.presales_cost_ids.filtered(lambda c: c.state != 'cancelled')
            rec.presales_cost_amount = sum(costs.mapped('amount'))

    def _compute_presales_counts(self):
        for rec in self:
            rec.requirement_count = len(rec.requirement_ids)
            rec.solution_scope_count = len(rec.solution_scope_ids)
            rec.estimate_count = len(rec.estimate_ids)
            rec.presales_cost_count = len(rec.presales_cost_ids)

    def _compute_quotation_count(self):
        Order = self.env['sale.order']
        for rec in self:
            domain = [('opportunity_id', '=', rec.id)] if rec.id else []
            rec.quotation_count = Order.search_count(domain) if rec.id else 0

    @api.depends('partner_id', 'estimated_revenue', 'estimate_ids.state')
    def _compute_quotation_ready(self):
        for rec in self:
            has_usable_estimate = bool(
                rec.estimate_ids.filtered(lambda e: e.is_approved_version or e.is_current_version)
            )
            rec.quotation_ready = bool(
                rec.partner_id and rec.estimated_revenue and has_usable_estimate
            )

    # ============================================================
    # Approval mixin overrides
    # ============================================================
    def _get_approval_type(self):
        self.ensure_one()
        return 'deal_approval'

    def _get_approval_amount(self):
        self.ensure_one()
        return self.estimated_revenue or self.expected_revenue or 0.0

    def _get_approval_department(self):
        self.ensure_one()
        owner = self.presales_owner_id or self.account_manager_id
        if owner:
            employee = self.env['hr.employee'].search([('user_id', '=', owner.id)], limit=1)
            if employee and employee.department_id:
                return employee.department_id
        return self.env['hr.department'].browse()

    def _validate_before_submit_approval(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please set a customer before submitting this deal for approval."))
        usable_estimate = self.approved_estimate_id or self.latest_estimate_id
        if not usable_estimate:
            raise UserError(_(
                "Please create at least one estimate before submitting this deal for approval."
            ))
        if not (self.estimated_revenue or 0.0) > 0:
            raise UserError(_("Estimated revenue must be greater than 0 before submitting for approval."))
        return True

    def _approval_approved_callback(self, request):
        self.ensure_one()
        super()._approval_approved_callback(request)
        self.write({'commercial_status': 'estimating' if not self.quotation_id else 'quoted'})

    def _approval_rejected_callback(self, request):
        self.ensure_one()
        super()._approval_rejected_callback(request)
        self.write({'commercial_status': 'estimating'})

    # ============================================================
    # Actions — Requirement
    # ============================================================
    def action_create_requirement(self):
        self.ensure_one()
        if self.commercial_status in ('draft', 'qualification'):
            self.commercial_status = 'surveying'
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Requirement Survey'),
            'res_model': 'dcg.crm.requirement',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_lead_id': self.id,
                'default_owner_id': (self.presales_owner_id or self.env.user).id,
            },
        }

    def action_view_requirements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Requirement Surveys'),
            'res_model': 'dcg.crm.requirement',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }

    # ============================================================
    # Actions — Solution Scope
    # ============================================================
    def action_view_solution_scope(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Solution Scope'),
            'res_model': 'dcg.crm.solution.scope',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }

    # ============================================================
    # Actions — Estimate
    # ============================================================
    def action_create_estimate(self):
        self.ensure_one()
        if self.commercial_status in ('draft', 'qualification', 'surveying'):
            self.commercial_status = 'estimating'
        next_version = 'V%d' % (len(self.estimate_ids) + 1)
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Estimate'),
            'res_model': 'dcg.crm.estimate',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_lead_id': self.id,
                'default_version': next_version,
                'default_owner_id': (self.presales_owner_id or self.env.user).id,
            },
        }

    def action_view_estimates(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Estimates'),
            'res_model': 'dcg.crm.estimate',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }

    # ============================================================
    # Actions — Presales Cost
    # ============================================================
    def action_view_presales_costs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Presales Costs'),
            'res_model': 'dcg.crm.presales.cost',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }

    # ============================================================
    # Actions — Quotation
    # ============================================================
    def action_create_quotation(self):
        """Tạo sale.order header từ lead; line do user bổ sung sau (Cách 1.5)."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please set a customer before creating a quotation."))
        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'opportunity_id': self.id,
            'currency_id': self.currency_id.id,
            'note': self.solution_scope_summary or '',
        })
        self.write({
            'quotation_id': order.id,
            'commercial_status': 'quoted',
        })
        usable_estimate = self.approved_estimate_id or self.latest_estimate_id
        if usable_estimate:
            usable_estimate.write({
                'quotation_id': order.id,
                'converted_to_quotation': True,
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quotations'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('opportunity_id', '=', self.id)],
            'context': {'default_opportunity_id': self.id, 'default_partner_id': self.partner_id.id},
        }

    # ============================================================
    # Actions — Won / Lost (presales-aware wrappers)
    # ============================================================
    def action_set_won_presales(self):
        for rec in self:
            rec.commercial_status = 'won'
        return self.action_set_won()

    def action_set_lost_presales(self, **kwargs):
        for rec in self:
            rec.commercial_status = 'lost'
        return True
