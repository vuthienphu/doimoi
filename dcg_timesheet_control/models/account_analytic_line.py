# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


WORK_TYPE_SELECTION = [
    ('project_delivery', 'Project Delivery'),
    ('support', 'Support'),
    ('internal', 'Internal'),
    ('presales', 'Presales'),
    ('training', 'Training'),
    ('leave_related', 'Leave Related'),
    ('other', 'Other'),
]

CHARGE_TYPE_SELECTION = [
    ('billable', 'Billable'),
    ('non_billable', 'Non-billable'),
    ('investment', 'Investment'),
]

LINE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # ============================================================
    # Sheet / approval
    # ============================================================
    dcg_sheet_id = fields.Many2one(
        'dcg.timesheet.sheet', string='Timesheet Sheet',
        index=True, ondelete='set null',
    )
    line_state = fields.Selection(
        selection=LINE_STATE_SELECTION, string='Line Status',
        default='draft', index=True,
    )

    # ============================================================
    # Delivery links
    # ============================================================
    dcg_project_id = fields.Many2one(
        'dcg.project.delivery', string='Delivery Project',
        index=True,
    )
    dcg_scope_id = fields.Many2one(
        'dcg.project.scope', string='Work Package',
        domain="[('project_id', '=', dcg_project_id)]",
    )
    dcg_milestone_id = fields.Many2one(
        'dcg.project.milestone', string='Milestone',
        domain="[('project_id', '=', dcg_project_id)]",
    )
    contract_id = fields.Many2one('dcg.contract', string='Contract')
    task_id = fields.Many2one('dcg.project.task', string='Task')

    # ============================================================
    # Classification
    # ============================================================
    work_type = fields.Selection(
        selection=WORK_TYPE_SELECTION, string='Work Type',
        default='project_delivery',
    )
    charge_type = fields.Selection(
        selection=CHARGE_TYPE_SELECTION, string='Charge Type',
        default='billable',
    )
    is_billable = fields.Boolean(
        string='Billable', compute='_compute_is_billable', store=True,
    )

    # ============================================================
    # Overtime
    # ============================================================
    is_overtime = fields.Boolean(string='Overtime')
    overtime_hours = fields.Float(string='OT Hours')
    ot_request_id = fields.Many2one(
        'dcg.timesheet.ot.request', string='OT Request',
    )

    # ============================================================
    # Content
    # ============================================================
    work_summary = fields.Text(string='Work Summary')
    result_note = fields.Text(string='Result')

    # ============================================================
    # Costing
    # ============================================================
    billing_rate = fields.Monetary(
        string='Billing Rate', currency_field='currency_id',
    )
    cost_rate = fields.Monetary(
        string='Cost Rate', currency_field='currency_id',
    )
    line_cost_amount = fields.Monetary(
        string='Cost Amount', currency_field='currency_id',
        compute='_compute_line_amounts', store=True,
    )
    line_billing_amount = fields.Monetary(
        string='Billing Amount', currency_field='currency_id',
        compute='_compute_line_amounts', store=True,
    )

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('charge_type')
    def _compute_is_billable(self):
        for rec in self:
            rec.is_billable = rec.charge_type == 'billable'

    @api.depends('unit_amount', 'cost_rate', 'billing_rate')
    def _compute_line_amounts(self):
        for rec in self:
            hours = rec.unit_amount or 0.0
            rec.line_cost_amount = hours * (rec.cost_rate or 0.0)
            rec.line_billing_amount = hours * (rec.billing_rate or 0.0)

    # ============================================================
    # Onchange helpers
    # ============================================================
    @api.onchange('dcg_project_id')
    def _onchange_dcg_project_id(self):
        if self.dcg_project_id:
            self.contract_id = self.dcg_project_id.contract_id
            if self.dcg_project_id.odoo_project_id:
                self.project_id = self.dcg_project_id.odoo_project_id
            # Reset scope/milestone when project changes
            self.dcg_scope_id = False
            self.dcg_milestone_id = False

    @api.onchange('task_id')
    def _onchange_task_id(self):
        if self.task_id:
            self.dcg_project_id = self.task_id.project_id
            self.dcg_scope_id = self.task_id.scope_id
            self.dcg_milestone_id = self.task_id.milestone_id
            self._onchange_dcg_project_id()

    @api.constrains('task_id')
    def _check_task_stage_allow_timesheet(self):
        for rec in self:
            if rec.task_id and not rec.task_id.stage_id.allow_timesheet:
                raise ValidationError(_("Cannot log timesheet on a task in this stage (%s).") % rec.task_id.stage_id.name)
