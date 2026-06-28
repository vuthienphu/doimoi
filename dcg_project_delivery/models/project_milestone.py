# -*- coding: utf-8 -*-
from odoo import fields, models


MILESTONE_TYPE_SELECTION = [
    ('kickoff', 'Kickoff'),
    ('survey', 'Survey'),
    ('analysis', 'Analysis / Blueprint'),
    ('development', 'Development'),
    ('uat', 'UAT'),
    ('training', 'Training'),
    ('go_live', 'Go Live'),
    ('acceptance', 'Acceptance'),
    ('other', 'Other'),
]

MILESTONE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('waiting', 'Waiting'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('delayed', 'Delayed'),
    ('cancelled', 'Cancelled'),
]


class DcgProjectMilestone(models.Model):
    _name = 'dcg.project.milestone'
    _description = 'Project Milestone'
    _inherit = ['mail.thread']
    _order = 'sequence, planned_date, id'

    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True,
    )
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Scope',
        domain="[('project_id', '=', project_id)]",
    )
    contract_payment_id = fields.Many2one(
        'dcg.contract.payment', string='Payment Milestone',
    )
    acceptance_id = fields.Many2one(
        'dcg.contract.acceptance', string='Acceptance',
    )

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Milestone', required=True)
    milestone_type = fields.Selection(
        selection=MILESTONE_TYPE_SELECTION, string='Type', default='other',
    )

    planned_date = fields.Date(string='Planned Date', tracking=True)
    actual_date = fields.Date(string='Actual Date')
    due_date = fields.Date(string='Due Date')

    state = fields.Selection(
        selection=MILESTONE_STATE_SELECTION, string='Status',
        default='draft', tracking=True,
    )
    progress_percent = fields.Float(string='Progress (%)')
    note = fields.Text(string='Note')

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done', 'actual_date': self.actual_date or fields.Date.today()})

    def action_delay(self):
        self.write({'state': 'delayed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
