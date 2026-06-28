# -*- coding: utf-8 -*-
from odoo import fields, models


ISSUE_TYPE_SELECTION = [
    ('issue', 'Issue'),
    ('risk', 'Risk'),
    ('blocker', 'Blocker'),
    ('dependency', 'Dependency'),
    ('customer_pending', 'Customer Pending'),
]

ISSUE_PRIORITY_SELECTION = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

ISSUE_STATE_SELECTION = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
    ('cancelled', 'Cancelled'),
]


class DcgProjectIssue(models.Model):
    _name = 'dcg.project.issue'
    _description = 'Project Issue / Risk / Blocker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True,
    )
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Scope',
        domain="[('project_id', '=', project_id)]",
    )
    milestone_id = fields.Many2one(
        'dcg.project.milestone', string='Milestone',
        domain="[('project_id', '=', project_id)]",
    )

    name = fields.Char(string='Title', required=True, tracking=True)
    issue_type = fields.Selection(
        selection=ISSUE_TYPE_SELECTION, string='Type',
        required=True, default='issue', tracking=True,
    )
    priority = fields.Selection(
        selection=ISSUE_PRIORITY_SELECTION, string='Priority',
        default='medium', tracking=True,
    )
    owner_id = fields.Many2one(
        'res.users', string='Assigned To', tracking=True,
    )
    raised_by_id = fields.Many2one(
        'res.users', string='Raised By', default=lambda self: self.env.user,
    )

    description = fields.Html(string='Description')
    impact = fields.Html(string='Impact')
    action_plan = fields.Html(string='Action Plan')
    target_date = fields.Date(string='Target Date')
    resolved_date = fields.Date(string='Resolved Date')
    state = fields.Selection(
        selection=ISSUE_STATE_SELECTION, string='Status',
        default='open', required=True, tracking=True,
    )

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        self.write({'state': 'resolved', 'resolved_date': fields.Date.today()})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reopen(self):
        self.write({'state': 'open', 'resolved_date': False})
