# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


OT_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class DcgTimesheetOtRequest(models.Model):
    _name = 'dcg.timesheet.ot.request'
    _description = 'Timesheet Overtime Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    name = fields.Char(
        string='OT Number', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        default=lambda self: self.env.user.employee_id, tracking=True,
    )
    user_id = fields.Many2one(
        'res.users', string='User', required=True,
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    request_date = fields.Date(
        string='Request Date', required=True,
        default=fields.Date.context_today, tracking=True,
    )
    date_from = fields.Datetime(string='OT Start', required=True)
    date_to = fields.Datetime(string='OT End', required=True)
    total_hours = fields.Float(
        string='OT Hours', compute='_compute_total_hours', store=True,
    )

    # Links
    project_id = fields.Many2one('dcg.project.delivery', string='Project')
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Scope',
        domain="[('project_id', '=', project_id)]",
    )
    reason = fields.Text(string='Reason', required=True)

    # State
    state = fields.Selection(
        selection=OT_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True,
    )
    approver_id = fields.Many2one('res.users', string='Approver', tracking=True)
    approved_date = fields.Datetime(string='Approved Date')
    reject_reason = fields.Text(string='Reject Reason')

    # Linked timesheet lines
    timesheet_line_ids = fields.One2many(
        'account.analytic.line', 'ot_request_id', string='Timesheet Lines',
    )

    @api.depends('date_from', 'date_to')
    def _compute_total_hours(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to > rec.date_from:
                delta = rec.date_to - rec.date_from
                rec.total_hours = delta.total_seconds() / 3600.0
            else:
                rec.total_hours = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.timesheet.ot.request')
                vals['name'] = seq or _('New')
            if not vals.get('approver_id') and vals.get('employee_id'):
                emp = self.env['hr.employee'].browse(vals['employee_id'])
                if emp.parent_id and emp.parent_id.user_id:
                    vals['approver_id'] = emp.parent_id.user_id.id
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft OT requests can be submitted."))
            rec.write({'state': 'submitted'})

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Only submitted OT requests can be approved."))
            rec.write({
                'state': 'approved',
                'approved_date': fields.Datetime.now(),
            })

    def action_reject(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Only submitted OT requests can be rejected."))
            rec.write({'state': 'rejected'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'approved':
                raise UserError(_("Cannot cancel an approved OT request."))
            rec.write({'state': 'cancelled'})
