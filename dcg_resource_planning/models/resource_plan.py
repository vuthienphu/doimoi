# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


PLAN_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
]


class DcgResourcePlan(models.Model):
    _name = 'dcg.resource.plan'
    _description = 'Resource Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Plan Code', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True, tracking=True,
    )
    contract_id = fields.Many2one(
        related='project_id.contract_id', string='Contract', store=True,
    )
    partner_id = fields.Many2one(
        related='project_id.partner_id', string='Customer', store=True,
    )
    manager_id = fields.Many2one(
        'res.users', string='Resource Manager', tracking=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    state = fields.Selection(
        selection=PLAN_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True,
    )

    # Lines
    allocation_ids = fields.One2many(
        'dcg.resource.allocation', 'plan_id', string='Allocations',
    )
    request_ids = fields.One2many(
        'dcg.resource.request', 'plan_id', string='Resource Requests',
    )

    # Summary
    planned_hours = fields.Float(
        string='Planned Hours',
        help='From project scope total hours.',
    )
    allocated_hours = fields.Float(
        string='Allocated Hours',
        compute='_compute_summary', store=True,
    )
    actual_hours = fields.Float(
        string='Actual Hours',
        compute='_compute_summary', store=True,
    )
    remaining_hours = fields.Float(
        string='Remaining Hours',
        compute='_compute_summary', store=True,
    )
    allocation_count = fields.Integer(compute='_compute_counts')
    request_count = fields.Integer(compute='_compute_counts')

    note = fields.Html(string='Note')

    _sql_constraints = [
        ('project_uniq', 'UNIQUE(project_id)',
         'A resource plan already exists for this project.'),
    ]

    @api.depends('allocation_ids.allocation_hours', 'project_id')
    def _compute_summary(self):
        Line = self.env['account.analytic.line']
        for rec in self:
            rec.allocated_hours = sum(rec.allocation_ids.mapped('allocation_hours'))
            if rec.project_id:
                actual = Line.search([
                    ('dcg_project_id', '=', rec.project_id.id),
                    ('line_state', '=', 'approved'),
                ])
                rec.actual_hours = sum(actual.mapped('unit_amount'))
            else:
                rec.actual_hours = 0
            rec.remaining_hours = (rec.planned_hours or 0) - rec.actual_hours

    def _compute_counts(self):
        for rec in self:
            rec.allocation_count = len(rec.allocation_ids)
            rec.request_count = len(rec.request_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.resource.plan')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def action_activate(self):
        self.write({'state': 'active'})

    def action_mark_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
