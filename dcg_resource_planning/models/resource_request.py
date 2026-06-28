# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


REQUEST_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('allocated', 'Allocated'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]

REQUEST_URGENCY_SELECTION = [
    ('critical', 'Critical'),
    ('high', 'High'),
    ('normal', 'Normal'),
    ('low', 'Low'),
]


class DcgResourceRequest(models.Model):
    _name = 'dcg.resource.request'
    _description = 'Resource Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Request No.', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    plan_id = fields.Many2one(
        'dcg.resource.plan', string='Resource Plan', index=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True, tracking=True,
    )
    requester_id = fields.Many2one(
        'res.users', string='Requester', required=True,
        default=lambda self: self.env.user, tracking=True,
    )
    approver_id = fields.Many2one(
        'res.users', string='Approver', tracking=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    state = fields.Selection(
        selection=REQUEST_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True,
    )

    # What is needed
    role_id = fields.Many2one(
        'dcg.resource.role', string='Role Needed', required=True,
    )
    quantity = fields.Integer(string='Quantity', default=1, required=True)
    urgency = fields.Selection(
        selection=REQUEST_URGENCY_SELECTION, string='Urgency', default='normal',
    )
    needed_from = fields.Date(string='Needed From', required=True)
    needed_until = fields.Date(string='Needed Until', required=True)
    allocation_percent = fields.Float(string='Allocation (%)', default=100.0)
    required_skills = fields.Text(string='Required Skills')
    justification = fields.Html(string='Justification')

    # Fulfillment
    allocated_employee_ids = fields.Many2many(
        'hr.employee', string='Allocated Employees',
        help='Employees assigned to fulfill this request.',
    )
    allocation_ids = fields.One2many(
        'dcg.resource.allocation', compute='_compute_allocation_ids',
    )
    fulfillment_note = fields.Text(string='Fulfillment Note')

    def _compute_allocation_ids(self):
        Alloc = self.env['dcg.resource.allocation']
        for rec in self:
            if rec.project_id and rec.role_id:
                rec.allocation_ids = Alloc.search([
                    ('project_id', '=', rec.project_id.id),
                    ('role_id', '=', rec.role_id.id),
                    ('state', '!=', 'cancelled'),
                ])
            else:
                rec.allocation_ids = Alloc

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.resource.request')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approved',
                'approver_id': self.env.uid,
            })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_mark_allocated(self):
        self.write({'state': 'allocated'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
