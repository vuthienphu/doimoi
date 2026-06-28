# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


FINANCE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('on_hold', 'On Hold'),
    ('done', 'Done'),
    ('closed', 'Closed'),
]

FINANCE_HEALTH_SELECTION = [
    ('green', 'Green'),
    ('yellow', 'Yellow'),
    ('red', 'Red'),
]


class DcgProjectFinance(models.Model):
    _name = 'dcg.project.finance'
    _description = 'Project Finance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Finance Code', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True, tracking=True,
    )
    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True, tracking=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True, default=lambda self: self.env.company.currency_id,
    )

    # Source snapshot
    lead_id = fields.Many2one('crm.lead', string='Opportunity')
    estimate_id = fields.Many2one('dcg.crm.estimate', string='Source Estimate')
    quotation_id = fields.Many2one('sale.order', string='Quotation')
    project_manager_id = fields.Many2one('res.users', string='PM', tracking=True)
    delivery_owner_id = fields.Many2one('res.users', string='Delivery Owner')

    # ============================================================
    # State
    # ============================================================
    state = fields.Selection(
        selection=FINANCE_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True, index=True,
    )
    finance_health = fields.Selection(
        selection=FINANCE_HEALTH_SELECTION, string='Finance Health',
        compute='_compute_finance_health', store=True, tracking=True,
    )
    freeze_snapshot = fields.Boolean(string='Freeze Planned')
    note = fields.Html(string='Note')

    # ============================================================
    # Planned / budget
    # ============================================================
    planned_revenue = fields.Monetary(string='Planned Revenue', currency_field='currency_id', tracking=True)
    planned_cost = fields.Monetary(string='Planned Cost', currency_field='currency_id', tracking=True)
    planned_labor_cost = fields.Monetary(string='Planned Labor Cost', currency_field='currency_id')
    planned_travel_cost = fields.Monetary(string='Planned Travel Cost', currency_field='currency_id')
    planned_subcontract_cost = fields.Monetary(string='Planned Subcontract Cost', currency_field='currency_id')
    planned_other_cost = fields.Monetary(string='Planned Other Cost', currency_field='currency_id')
    planned_margin = fields.Monetary(
        string='Planned Margin', currency_field='currency_id',
        compute='_compute_planned_summary', store=True,
    )
    planned_margin_rate = fields.Float(
        string='Planned Margin (%)', compute='_compute_planned_summary', store=True,
    )

    # ============================================================
    # Actual
    # ============================================================
    actual_revenue = fields.Monetary(
        string='Actual Revenue', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_cost = fields.Monetary(
        string='Actual Cost', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_labor_cost = fields.Monetary(
        string='Actual Labor Cost', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_travel_cost = fields.Monetary(
        string='Actual Travel Cost', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_subcontract_cost = fields.Monetary(
        string='Actual Subcontract Cost', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_other_cost = fields.Monetary(
        string='Actual Other Cost', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_margin = fields.Monetary(
        string='Actual Margin', currency_field='currency_id',
        compute='_compute_actual_summary', store=True,
    )
    actual_margin_rate = fields.Float(
        string='Actual Margin (%)', compute='_compute_actual_summary', store=True,
    )

    # ============================================================
    # Collection
    # ============================================================
    invoiced_amount = fields.Monetary(
        string='Invoiced', currency_field='currency_id',
        compute='_compute_collection', store=True,
    )
    collected_amount = fields.Monetary(
        string='Collected', currency_field='currency_id',
        compute='_compute_collection', store=True,
    )
    uncollected_amount = fields.Monetary(
        string='Outstanding', currency_field='currency_id',
        compute='_compute_collection', store=True,
    )
    collection_rate = fields.Float(
        string='Collection Rate (%)', compute='_compute_collection', store=True,
    )

    # ============================================================
    # Effort
    # ============================================================
    planned_hours = fields.Float(string='Planned Hours')
    actual_hours = fields.Float(
        string='Actual Hours', compute='_compute_effort', store=True,
    )
    billable_hours = fields.Float(
        string='Billable Hours', compute='_compute_effort', store=True,
    )
    non_billable_hours = fields.Float(
        string='Non-billable Hours', compute='_compute_effort', store=True,
    )
    ot_hours = fields.Float(
        string='OT Hours', compute='_compute_effort', store=True,
    )
    avg_cost_per_hour = fields.Monetary(
        string='Avg Cost/Hour', currency_field='currency_id',
        compute='_compute_effort', store=True,
    )

    # ============================================================
    # Variance
    # ============================================================
    revenue_variance = fields.Monetary(
        string='Revenue Variance', currency_field='currency_id',
        compute='_compute_variance', store=True,
    )
    cost_variance = fields.Monetary(
        string='Cost Variance', currency_field='currency_id',
        compute='_compute_variance', store=True,
    )
    margin_variance = fields.Monetary(
        string='Margin Variance', currency_field='currency_id',
        compute='_compute_variance', store=True,
    )
    hours_variance = fields.Float(
        string='Hours Variance', compute='_compute_variance', store=True,
    )
    warning_note = fields.Html(string='Warning Note')

    # ============================================================
    # Lines
    # ============================================================
    cost_line_ids = fields.One2many(
        'dcg.project.finance.cost.line', 'finance_id', string='Cost Lines',
    )
    revenue_line_ids = fields.One2many(
        'dcg.project.finance.revenue.line', 'finance_id', string='Revenue Lines',
    )
    cost_line_count = fields.Integer(compute='_compute_line_counts')
    revenue_line_count = fields.Integer(compute='_compute_line_counts')

    # ============================================================
    # Constraints
    # ============================================================
    _sql_constraints = [
        ('project_uniq', 'UNIQUE(project_id)',
         'A finance record already exists for this project.'),
    ]

    # ============================================================
    # Compute: planned
    # ============================================================
    @api.depends('planned_revenue', 'planned_cost')
    def _compute_planned_summary(self):
        for rec in self:
            rec.planned_margin = (rec.planned_revenue or 0) - (rec.planned_cost or 0)
            rec.planned_margin_rate = (
                rec.planned_margin / rec.planned_revenue * 100
                if rec.planned_revenue else 0
            )

    # ============================================================
    # Compute: actual (from cost/revenue lines)
    # ============================================================
    @api.depends('cost_line_ids.amount', 'cost_line_ids.cost_type',
                 'revenue_line_ids.invoiced_amount')
    def _compute_actual_summary(self):
        for rec in self:
            costs = rec.cost_line_ids
            rec.actual_labor_cost = sum(l.amount for l in costs if l.cost_type == 'labor')
            rec.actual_travel_cost = sum(l.amount for l in costs if l.cost_type == 'travel')
            rec.actual_subcontract_cost = sum(l.amount for l in costs if l.cost_type == 'subcontract')
            rec.actual_other_cost = sum(
                l.amount for l in costs if l.cost_type not in ('labor', 'travel', 'subcontract')
            )
            rec.actual_cost = sum(costs.mapped('amount'))
            rec.actual_revenue = sum(rec.revenue_line_ids.mapped('invoiced_amount'))
            rec.actual_margin = rec.actual_revenue - rec.actual_cost
            rec.actual_margin_rate = (
                rec.actual_margin / rec.actual_revenue * 100
                if rec.actual_revenue else 0
            )

    # ============================================================
    # Compute: collection
    # ============================================================
    @api.depends('revenue_line_ids.invoiced_amount', 'revenue_line_ids.collected_amount',
                 'planned_revenue')
    def _compute_collection(self):
        for rec in self:
            rlines = rec.revenue_line_ids
            rec.invoiced_amount = sum(rlines.mapped('invoiced_amount'))
            rec.collected_amount = sum(rlines.mapped('collected_amount'))
            rec.uncollected_amount = rec.invoiced_amount - rec.collected_amount
            rec.collection_rate = (
                rec.collected_amount / rec.planned_revenue * 100
                if rec.planned_revenue else 0
            )

    # ============================================================
    # Compute: effort
    # ============================================================
    @api.depends('project_id')
    def _compute_effort(self):
        Line = self.env['account.analytic.line']
        for rec in self:
            if not rec.project_id:
                rec.actual_hours = rec.billable_hours = rec.non_billable_hours = 0
                rec.ot_hours = rec.avg_cost_per_hour = 0
                continue
            domain = [
                ('dcg_project_id', '=', rec.project_id.id),
                ('line_state', '=', 'approved'),
            ]
            lines = Line.search(domain)
            rec.actual_hours = sum(lines.mapped('unit_amount'))
            rec.billable_hours = sum(l.unit_amount for l in lines if l.charge_type == 'billable')
            rec.non_billable_hours = sum(l.unit_amount for l in lines if l.charge_type != 'billable')
            rec.ot_hours = sum(
                l.overtime_hours or l.unit_amount for l in lines if l.is_overtime
            )
            rec.avg_cost_per_hour = (
                rec.actual_labor_cost / rec.actual_hours if rec.actual_hours else 0
            )

    # ============================================================
    # Compute: variance
    # ============================================================
    @api.depends('planned_revenue', 'actual_revenue', 'planned_cost', 'actual_cost',
                 'planned_margin', 'actual_margin', 'planned_hours', 'actual_hours')
    def _compute_variance(self):
        for rec in self:
            rec.revenue_variance = (rec.actual_revenue or 0) - (rec.planned_revenue or 0)
            rec.cost_variance = (rec.actual_cost or 0) - (rec.planned_cost or 0)
            rec.margin_variance = (rec.actual_margin or 0) - (rec.planned_margin or 0)
            rec.hours_variance = (rec.actual_hours or 0) - (rec.planned_hours or 0)

    # ============================================================
    # Compute: finance health (spec mục 67-68)
    # ============================================================
    @api.depends('actual_margin', 'actual_cost', 'planned_cost',
                 'collection_rate', 'planned_revenue')
    def _compute_finance_health(self):
        for rec in self:
            if rec.actual_margin and rec.actual_margin < 0:
                rec.finance_health = 'red'
            elif rec.planned_cost and rec.actual_cost > rec.planned_cost * 1.15:
                rec.finance_health = 'red'
            elif rec.planned_cost and rec.actual_cost > rec.planned_cost:
                rec.finance_health = 'yellow'
            elif rec.planned_revenue and rec.collection_rate < 30 and rec.actual_hours > (rec.planned_hours or 1) * 0.8:
                rec.finance_health = 'yellow'
            else:
                rec.finance_health = 'green'

    def _compute_line_counts(self):
        for rec in self:
            rec.cost_line_count = len(rec.cost_line_ids)
            rec.revenue_line_count = len(rec.revenue_line_ids)

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.project.finance')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    # ============================================================
    # State actions
    # ============================================================
    def action_activate(self):
        self.write({'state': 'active'})

    def action_set_on_hold(self):
        self.write({'state': 'on_hold'})

    def action_mark_done(self):
        self.write({'state': 'done'})

    def action_close(self):
        for rec in self:
            if rec.state != 'done':
                raise UserError(_("Finance record must be done before closing."))
            rec.write({'state': 'closed'})

    # ============================================================
    # Sync actions
    # ============================================================
    def action_sync_revenue_from_contract(self):
        """Sync revenue lines from contract payment schedule (spec mục 47)."""
        self.ensure_one()
        RevLine = self.env['dcg.project.finance.revenue.line']
        for payment in self.contract_id.payment_ids:
            existing = RevLine.search([
                ('finance_id', '=', self.id),
                ('payment_id', '=', payment.id),
            ], limit=1)
            vals = {
                'finance_id': self.id,
                'project_id': self.project_id.id,
                'contract_id': self.contract_id.id,
                'payment_id': payment.id,
                'name': payment.name,
                'line_type': 'contract_value',
                'planned_amount': payment.amount,
                'revenue_date': payment.due_date or payment.planned_invoice_date,
                'invoiced_amount': payment.amount_received if payment.state == 'paid' else 0,
                'collected_amount': payment.amount_received if payment.state == 'paid' else 0,
                'state': 'collected' if payment.state == 'paid' else (
                    'invoiced' if payment.state in ('waiting', 'partial') else 'planned'
                ),
            }
            if existing:
                existing.write(vals)
            else:
                RevLine.create(vals)

    def action_refresh_actual_cost(self):
        """Sync labor cost lines from approved timesheet (spec mục 54)."""
        self.ensure_one()
        CostLine = self.env['dcg.project.finance.cost.line']
        TimeLine = self.env['account.analytic.line']
        approved_lines = TimeLine.search([
            ('dcg_project_id', '=', self.project_id.id),
            ('line_state', '=', 'approved'),
        ])
        for tl in approved_lines:
            existing = CostLine.search([
                ('finance_id', '=', self.id),
                ('timesheet_line_id', '=', tl.id),
            ], limit=1)
            vals = {
                'finance_id': self.id,
                'project_id': self.project_id.id,
                'contract_id': self.contract_id.id,
                'scope_id': tl.dcg_scope_id.id if tl.dcg_scope_id else False,
                'cost_type': 'labor',
                'source_type': 'timesheet',
                'timesheet_line_id': tl.id,
                'name': tl.name or _('Timesheet'),
                'cost_date': tl.date,
                'amount': tl.line_cost_amount or 0,
                'employee_id': tl.employee_id.id if tl.employee_id else False,
                'currency_id': self.currency_id.id,
            }
            if existing:
                existing.write(vals)
            else:
                CostLine.create(vals)

    def action_recompute_summary(self):
        """Force recompute all summary fields."""
        self._compute_actual_summary()
        self._compute_collection()
        self._compute_effort()
        self._compute_variance()
        self._compute_finance_health()

    # Navigation
    def action_view_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.project.delivery',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_contract(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.contract',
            'res_id': self.contract_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
