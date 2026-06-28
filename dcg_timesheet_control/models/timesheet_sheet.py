# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


PERIOD_TYPE_SELECTION = [
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('manual', 'Manual'),
]

SHEET_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class DcgTimesheetSheet(models.Model):
    _name = 'dcg.timesheet.sheet'
    _description = 'Timesheet Sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'
    _rec_name = 'name'

    # ============================================================
    # Identification
    # ============================================================
    name = fields.Char(
        string='Sheet Number', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, tracking=True,
        default=lambda self: self.env.user.employee_id,
    )
    user_id = fields.Many2one(
        'res.users', string='User', required=True,
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    date_start = fields.Date(string='Period Start', required=True, tracking=True)
    date_end = fields.Date(string='Period End', required=True, tracking=True)
    period_type = fields.Selection(
        selection=PERIOD_TYPE_SELECTION, string='Period Type',
        required=True, default='weekly',
    )
    week_no = fields.Integer(string='Week No.', compute='_compute_period_info', store=True)
    month_key = fields.Char(string='Month', compute='_compute_period_info', store=True)

    # ============================================================
    # State / approval
    # ============================================================
    state = fields.Selection(
        selection=SHEET_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True, index=True,
    )
    approver_id = fields.Many2one(
        'res.users', string='Approver', tracking=True,
    )
    submitted_date = fields.Datetime(string='Submitted Date')
    approved_date = fields.Datetime(string='Approved Date')
    rejected_date = fields.Datetime(string='Rejected Date')
    reject_reason = fields.Text(string='Reject Reason')
    note = fields.Text(string='Note')

    # ============================================================
    # Lines
    # ============================================================
    line_ids = fields.One2many(
        'account.analytic.line', 'dcg_sheet_id', string='Timesheet Lines',
    )

    # ============================================================
    # Summary (compute)
    # ============================================================
    total_hours = fields.Float(compute='_compute_totals', store=True, string='Total Hours')
    total_billable_hours = fields.Float(compute='_compute_totals', store=True, string='Billable Hours')
    total_non_billable_hours = fields.Float(compute='_compute_totals', store=True, string='Non-billable Hours')
    total_ot_hours = fields.Float(compute='_compute_totals', store=True, string='OT Hours')
    line_count = fields.Integer(compute='_compute_totals', store=True, string='Lines')

    # ============================================================
    # Constraints
    # ============================================================
    _sql_constraints = [
        ('employee_period_uniq',
         'UNIQUE(employee_id, date_start, date_end)',
         'A timesheet sheet already exists for this employee and period.'),
    ]

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_("Period start must be before period end."))

    # ============================================================
    # Compute
    # ============================================================
    @api.depends('date_start')
    def _compute_period_info(self):
        for rec in self:
            if rec.date_start:
                rec.week_no = rec.date_start.isocalendar()[1]
                rec.month_key = rec.date_start.strftime('%Y-%m')
            else:
                rec.week_no = 0
                rec.month_key = ''

    @api.depends(
        'line_ids.unit_amount',
        'line_ids.charge_type',
        'line_ids.is_overtime',
        'line_ids.overtime_hours',
    )
    def _compute_totals(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_hours = sum(lines.mapped('unit_amount'))
            rec.total_billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type == 'billable'
            )
            rec.total_non_billable_hours = sum(
                l.unit_amount for l in lines if l.charge_type != 'billable'
            )
            rec.total_ot_hours = sum(
                l.overtime_hours or l.unit_amount for l in lines if l.is_overtime
            )
            rec.line_count = len(lines)

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.timesheet.sheet')
                vals['name'] = seq or _('New')
            # Default approver = employee's manager
            if not vals.get('approver_id') and vals.get('employee_id'):
                emp = self.env['hr.employee'].browse(vals['employee_id'])
                if emp.parent_id and emp.parent_id.user_id:
                    vals['approver_id'] = emp.parent_id.user_id.id
        return super().create(vals_list)

    # ============================================================
    # Actions
    # ============================================================
    def action_load_lines(self):
        """Nạp line draft chưa gán sheet của employee trong kỳ (spec mục 19, 20)."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Can only load lines into a draft sheet."))
        Line = self.env['account.analytic.line']
        domain = [
            ('user_id', '=', self.user_id.id),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('dcg_sheet_id', '=', False),
            ('project_id', '!=', False),  # only timesheet lines
        ]
        lines = Line.search(domain)
        lines.write({'dcg_sheet_id': self.id})
        return True

    def action_submit(self):
        """Submit sheet + sync line_state (spec mục 21, 58)."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft sheets can be submitted."))
            if not rec.line_ids:
                raise UserError(_("Cannot submit an empty timesheet sheet."))
            rec.write({
                'state': 'submitted',
                'submitted_date': fields.Datetime.now(),
            })
            rec.line_ids.write({'line_state': 'submitted'})

    def action_approve(self):
        """Approve sheet + sync line_state, trigger project actual recompute."""
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Only submitted sheets can be approved."))
            rec.write({
                'state': 'approved',
                'approved_date': fields.Datetime.now(),
            })
            rec.line_ids.write({'line_state': 'approved'})

    def action_reject(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Only submitted sheets can be rejected."))
            rec.write({
                'state': 'rejected',
                'rejected_date': fields.Datetime.now(),
            })
            rec.line_ids.write({'line_state': 'rejected'})

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state not in ('submitted', 'rejected', 'approved'):
                raise UserError(_("Cannot reset this sheet to draft."))
            rec.write({
                'state': 'draft',
                'submitted_date': False,
                'approved_date': False,
                'rejected_date': False,
                'reject_reason': False,
            })
            rec.line_ids.write({'line_state': 'draft'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'approved':
                raise UserError(_("Cannot cancel an approved sheet. Reset to draft first."))
            rec.write({'state': 'cancelled'})
            rec.line_ids.write({'dcg_sheet_id': False, 'line_state': 'draft'})
