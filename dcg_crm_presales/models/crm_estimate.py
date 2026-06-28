# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


ESTIMATE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('review', 'In Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('archived', 'Archived'),
]


class DcgCrmEstimate(models.Model):
    """Một phiên bản estimate effort/cost/revenue/timeline cho opportunity.

    Approval (phase 1) bám vào crm.lead, không bám vào estimate trực tiếp.
    Estimate vẫn có sẵn field approval_required/approval_state/approval_request_id
    để dễ chuyển sang approval-per-estimate ở phase sau mà không đổi schema.
    """
    _name = 'dcg.crm.estimate'
    _description = 'CRM Presales Estimate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    # ============================================================
    # Header
    # ============================================================
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        required=True,
        ondelete='cascade',
        index=True,
        domain="[('type', '=', 'opportunity')]",
        tracking=True,
    )
    partner_id = fields.Many2one(
        related='lead_id.partner_id',
        string='Customer',
        store=True,
        readonly=True,
    )
    version = fields.Char(string='Version', required=True, default='V1', tracking=True)
    estimate_date = fields.Date(
        string='Estimate Date',
        default=fields.Date.context_today,
        tracking=True,
    )
    owner_id = fields.Many2one(
        'res.users',
        string='Estimated By',
        default=lambda self: self.env.user,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    state = fields.Selection(
        selection=ESTIMATE_STATE_SELECTION,
        string='Status',
        default='draft',
        tracking=True,
        index=True,
    )
    is_current_version = fields.Boolean(
        string='Current Version',
        tracking=True,
        help='The version currently being worked on / referenced as the latest.',
    )
    is_approved_version = fields.Boolean(
        string='Approved Version',
        tracking=True,
        help='The version chosen by the business as the basis for quotation.',
    )

    # ============================================================
    # Lines
    # ============================================================
    line_ids = fields.One2many(
        'dcg.crm.estimate.line',
        'estimate_id',
        string='Estimate Lines',
        copy=True,
    )
    line_count = fields.Integer(string='Line Count', compute='_compute_line_count')

    # ============================================================
    # Effort summary (aggregated from lines, manual fallback if no lines)
    # ============================================================
    estimated_ba_hours = fields.Float(string='BA Hours', compute='_compute_effort_summary', store=True)
    estimated_dev_hours = fields.Float(string='Dev Hours', compute='_compute_effort_summary', store=True)
    estimated_test_hours = fields.Float(string='Test Hours', compute='_compute_effort_summary', store=True)
    estimated_pm_hours = fields.Float(string='PM Hours', compute='_compute_effort_summary', store=True)
    estimated_support_hours = fields.Float(string='Support Hours', compute='_compute_effort_summary', store=True)
    estimated_other_hours = fields.Float(string='Other Hours', compute='_compute_effort_summary', store=True)
    total_estimated_hours = fields.Float(string='Total Hours', compute='_compute_effort_summary', store=True)

    # ============================================================
    # Commercial summary
    # ============================================================
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id', tracking=True)
    estimated_revenue = fields.Monetary(string='Estimated Revenue', currency_field='currency_id', tracking=True)
    estimated_margin = fields.Monetary(
        string='Estimated Margin', currency_field='currency_id', compute='_compute_margin', store=True
    )
    estimated_margin_rate = fields.Float(
        string='Margin Rate (%)', compute='_compute_margin', store=True
    )
    estimated_timeline_days = fields.Integer(string='Timeline (days)')
    estimated_timeline_note = fields.Text(string='Timeline Note')

    # ============================================================
    # Scope / explanation
    # ============================================================
    scope_summary = fields.Html(string='Scope Summary')
    assumption_note = fields.Html(string='Assumptions')
    exclusion_note = fields.Html(string='Exclusions')
    risk_note = fields.Text(string='Risk Note')
    pricing_note = fields.Text(string='Pricing Note')

    # ============================================================
    # Approval / quotation (forward-compatible, not used by phase-1 engine)
    # ============================================================
    approval_required = fields.Boolean(string='Approval Required')
    approval_request_id = fields.Many2one(
        'dcg.approval.request',
        string='Approval Request',
        copy=False,
        readonly=True,
    )
    approval_state = fields.Selection(
        selection=[
            ('not_required', 'Not Required'),
            ('draft', 'Draft'),
            ('waiting', 'Waiting Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        string='Approval Status',
        default='not_required',
        copy=False,
    )
    quotation_id = fields.Many2one('sale.order', string='Quotation', copy=False, readonly=True)
    converted_to_quotation = fields.Boolean(string='Converted to Quotation', copy=False)

    _sql_constraints = [
        (
            'name_lead_uniq',
            'unique(lead_id, version)',
            'Estimate version must be unique per opportunity.',
        ),
    ]

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.depends(
        'line_ids.ba_hours', 'line_ids.dev_hours', 'line_ids.test_hours',
        'line_ids.pm_hours', 'line_ids.support_hours', 'line_ids.other_hours',
    )
    def _compute_effort_summary(self):
        for rec in self:
            lines = rec.line_ids
            rec.estimated_ba_hours = sum(lines.mapped('ba_hours'))
            rec.estimated_dev_hours = sum(lines.mapped('dev_hours'))
            rec.estimated_test_hours = sum(lines.mapped('test_hours'))
            rec.estimated_pm_hours = sum(lines.mapped('pm_hours'))
            rec.estimated_support_hours = sum(lines.mapped('support_hours'))
            rec.estimated_other_hours = sum(lines.mapped('other_hours'))
            rec.total_estimated_hours = sum(lines.mapped('total_hours'))

    @api.depends('estimated_revenue', 'estimated_cost')
    def _compute_margin(self):
        for rec in self:
            rec.estimated_margin = (rec.estimated_revenue or 0.0) - (rec.estimated_cost or 0.0)
            if rec.estimated_revenue:
                rec.estimated_margin_rate = (rec.estimated_margin / rec.estimated_revenue) * 100.0
            else:
                rec.estimated_margin_rate = 0.0

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.crm.estimate')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    # ============================================================
    # Actions
    # ============================================================
    def action_set_current_version(self):
        """Đánh dấu estimate này là current version; clear flag ở estimate khác cùng lead."""
        for rec in self:
            siblings = self.search([
                ('lead_id', '=', rec.lead_id.id),
                ('id', '!=', rec.id),
            ])
            siblings.write({'is_current_version': False})
            rec.is_current_version = True
            rec._sync_to_lead()
        return True

    def action_mark_approved_version(self):
        """Đánh dấu estimate này là approved version (chốt để báo giá)."""
        for rec in self:
            siblings = self.search([
                ('lead_id', '=', rec.lead_id.id),
                ('id', '!=', rec.id),
            ])
            siblings.write({'is_approved_version': False})
            rec.write({'is_approved_version': True, 'state': 'approved'})
            rec.lead_id.write({'approved_estimate_id': rec.id})
            rec._sync_to_lead()
        return True

    def action_set_review(self):
        self.write({'state': 'review'})
        return True

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_archive_estimate(self):
        self.write({
            'state': 'archived',
            'is_current_version': False,
            'is_approved_version': False,
        })
        return True

    def _sync_to_lead(self):
        """Đẩy summary của estimate này lên lead (gọi khi set current/approved)."""
        self.ensure_one()
        lead = self.lead_id
        lead.write({
            'latest_estimate_id': self.id,
            'estimated_ba_hours': self.estimated_ba_hours,
            'estimated_dev_hours': self.estimated_dev_hours,
            'estimated_test_hours': self.estimated_test_hours,
            'estimated_pm_hours': self.estimated_pm_hours,
            'estimated_support_hours': self.estimated_support_hours,
            'estimated_timeline_days': self.estimated_timeline_days,
            'estimated_cost': self.estimated_cost,
            'estimated_revenue': self.estimated_revenue,
            'solution_scope_summary': self.scope_summary,
        })

    def action_view_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
