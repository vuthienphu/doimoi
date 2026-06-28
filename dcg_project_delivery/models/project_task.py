# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

TASK_TYPE_SELECTION = [
    ('ba', 'BA / Analysis'),
    ('dev', 'Development'),
    ('qa', 'Testing / QA'),
    ('review', 'Code Review'),
    ('deploy', 'Deployment'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('other', 'Other'),
]

TASK_PRIORITY_SELECTION = [
    ('low', 'Low'),
    ('normal', 'Normal'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

TASK_KANBAN_STATE_SELECTION = [
    ('normal', 'In Progress'),
    ('blocked', 'Blocked'),
    ('ready', 'Ready for Review'),
]

CHARGE_TYPE_SELECTION = [
    ('billable', 'Billable'),
    ('non_billable', 'Non-billable'),
    ('investment', 'Investment'),
]


class DcgProjectTask(models.Model):
    _name = 'dcg.project.task'
    _description = 'Project Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, planned_end, id'
    _rec_name = 'name'

    name = fields.Char(string='Task Name', required=True, tracking=True)
    code = fields.Char(
        string='Task Code', index=True, copy=False,
        default=lambda self: _('New'), readonly=True,
    )
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company,
    )
    color = fields.Integer(string='Color')
    kanban_state = fields.Selection(
        selection=TASK_KANBAN_STATE_SELECTION, string='Kanban State',
        default='normal', tracking=True,
    )
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', tracking=True, index=True,
    )
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Work Package',
        domain="[('project_id', '=', project_id)]",
    )
    milestone_id = fields.Many2one(
        'dcg.project.milestone', string='Milestone',
        domain="[('project_id', '=', project_id)]",
    )
    contract_id = fields.Many2one(
        'dcg.contract', string='Contract',
        related='project_id.contract_id', readonly=True, store=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        related='project_id.partner_id', readonly=True, store=True,
    )
    stage_id = fields.Many2one(
        'dcg.project.task.stage', string='Stage', required=True,
        tracking=True, index=True,
        default=lambda self: self.env['dcg.project.task.stage'].search([('is_start', '=', True)], limit=1).id,
    )
    is_done = fields.Boolean(
        string='Done', related='stage_id.is_done', readonly=True, store=True,
    )
    is_cancel = fields.Boolean(
        string='Cancelled', related='stage_id.is_cancel', readonly=True, store=True,
    )
    task_type = fields.Selection(
        selection=TASK_TYPE_SELECTION, string='Task Type',
        required=True, default='other', tracking=True,
    )
    priority = fields.Selection(
        selection=TASK_PRIORITY_SELECTION, string='Priority',
        default='normal', tracking=True,
    )
    assignee_id = fields.Many2one(
        'res.users', string='Assignee', required=True, tracking=True,
    )
    assignee_ids = fields.Many2many(
        'res.users', 'dcg_project_task_users_rel', 'task_id', 'user_id',
        string='Co-Assignees',
    )
    reviewer_id = fields.Many2one(
        'res.users', string='Reviewer', tracking=True,
    )
    planned_start = fields.Datetime(string='Planned Start')
    planned_end = fields.Datetime(string='Planned End (Deadline)')
    actual_start = fields.Datetime(string='Actual Start', readonly=True)
    actual_end = fields.Datetime(string='Actual End', readonly=True)
    planned_hours = fields.Float(string='Planned Hours')
    actual_hours = fields.Float(
        string='Actual Hours', compute='_compute_hours', store=True,
    )
    remaining_hours = fields.Float(
        string='Remaining Hours', compute='_compute_hours', store=True,
    )
    progress_percent = fields.Float(string='Progress (%)')
    is_overdue = fields.Boolean(
        string='Overdue', compute='_compute_is_overdue', store=True,
    )
    is_billable = fields.Boolean(string='Billable', default=True)
    charge_type = fields.Selection(
        selection=CHARGE_TYPE_SELECTION, string='Charge Type',
        default='billable',
    )
    description = fields.Html(string='Description')
    acceptance_criteria = fields.Html(string='Acceptance Criteria')
    result_note = fields.Html(string='Result Note')
    reject_reason = fields.Text(string='Reject Reason')
    tag_ids = fields.Many2many(
        'dcg.project.task.tag', 'dcg_project_task_tag_rel', 'task_id', 'tag_id',
        string='Tags',
    )
    timesheet_line_ids = fields.One2many(
        'account.analytic.line', 'task_id', string='Timesheets',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_project_task_attachment_rel', 'task_id', 'attachment_id',
        string='Attachments',
    )
    timesheet_count = fields.Integer(
        string='Timesheets', compute='_compute_timesheet_count',
    )
    child_task_ids = fields.One2many(
        'dcg.project.task', 'parent_id', string='Sub-tasks',
    )
    parent_id = fields.Many2one(
        'dcg.project.task', string='Parent Task', ondelete='cascade',
    )
    child_count = fields.Integer(
        string='Sub-tasks Count', compute='_compute_child_count',
    )

    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_hours(self):
        for rec in self:
            actual = sum(rec.timesheet_line_ids.mapped('unit_amount'))
            rec.actual_hours = actual
            rec.remaining_hours = (rec.planned_hours or 0.0) - actual

    @api.depends('planned_end', 'is_done')
    def _compute_is_overdue(self):
        today = fields.Datetime.now()
        for rec in self:
            if rec.planned_end and rec.planned_end < today and not rec.is_done:
                rec.is_overdue = True
            else:
                rec.is_overdue = False

    def _compute_timesheet_count(self):
        for rec in self:
            rec.timesheet_count = len(rec.timesheet_line_ids)

    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_task_ids)

    # Constraints / Business Rules
    @api.constrains('assignee_id', 'project_id')
    def _check_assignee_in_project_members(self):
        for rec in self:
            if rec.assignee_id and rec.project_id:
                member_user_ids = rec.project_id.member_ids.mapped('user_id.id')
                if rec.assignee_id.id not in member_user_ids:
                    raise ValidationError(_("Assignee must be a member of the project."))

    @api.constrains('scope_id', 'project_id')
    def _check_scope_in_project(self):
        for rec in self:
            if rec.scope_id and rec.scope_id.project_id != rec.project_id:
                raise ValidationError(_("Work Package must belong to the selected project."))

    @api.constrains('milestone_id', 'project_id')
    def _check_milestone_in_project(self):
        for rec in self:
            if rec.milestone_id and rec.milestone_id.project_id != rec.project_id:
                raise ValidationError(_("Milestone must belong to the selected project."))

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.project_id = self.parent_id.project_id
            self.scope_id = self.parent_id.scope_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.project.task')
                vals['code'] = seq or _('New')
            # Trigger actual_start when created directly in active stage
            if vals.get('stage_id'):
                stage = self.env['dcg.project.task.stage'].browse(vals['stage_id'])
                if not stage.is_start and not stage.is_done and not stage.is_cancel:
                    vals['actual_start'] = fields.Datetime.now()
                elif stage.is_done:
                    vals['actual_end'] = fields.Datetime.now()
                    vals['progress_percent'] = 100.0
        return super().create(vals_list)

    def write(self, vals):
        # Prevent editing if is_cancel = True
        for rec in self:
            if rec.is_cancel and any(field not in ['active'] for field in vals):
                raise ValidationError(_("Cannot modify a cancelled task."))

        # Detect stage change
        if 'stage_id' in vals:
            stage = self.env['dcg.project.task.stage'].browse(vals['stage_id'])
            for rec in self:
                # To Do -> In Progress
                if not stage.is_start and not stage.is_done and not stage.is_cancel:
                    if not rec.actual_start:
                        vals['actual_start'] = fields.Datetime.now()
                # -> Done
                elif stage.is_done:
                    if not rec.actual_end:
                        vals['actual_end'] = fields.Datetime.now()
                    vals['progress_percent'] = 100.0
                # -> Cancelled
                elif stage.is_cancel:
                    pass

        # Detect kanban_state blocked notification
        if vals.get('kanban_state') == 'blocked':
            for rec in self:
                rec._notify_blocked()

        return super().write(vals)

    def action_mark_done(self):
        done_stage = self.env['dcg.project.task.stage'].search([('is_done', '=', True)], limit=1)
        if done_stage:
            self.write({'stage_id': done_stage.id})

    def action_cancel(self):
        cancel_stage = self.env['dcg.project.task.stage'].search([('is_cancel', '=', True)], limit=1)
        if cancel_stage:
            self.write({'stage_id': cancel_stage.id})

    def _notify_blocked(self):
        partner_ids = []
        if self.assignee_id.partner_id:
            partner_ids.append(self.assignee_id.partner_id.id)
        if self.project_id.project_manager_id.partner_id:
            partner_ids.append(self.project_id.project_manager_id.partner_id.id)
        if partner_ids:
            self.message_post(
                body=_("Task %s is BLOCKED!") % self.name,
                partner_ids=partner_ids,
                message_type='notification',
            )


class DcgProjectTaskStage(models.Model):
    _name = 'dcg.project.task.stage'
    _description = 'Project Task Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    fold = fields.Boolean(string='Folded in Kanban')
    is_start = fields.Boolean(string='Start Stage')
    is_done = fields.Boolean(string='Done Stage')
    is_cancel = fields.Boolean(string='Cancel Stage')
    allow_timesheet = fields.Boolean(string='Allow Timesheet')
    color = fields.Integer(string='Color')
    description = fields.Text(string='Description')


class DcgProjectTaskTag(models.Model):
    _name = 'dcg.project.task.tag'
    _description = 'Project Task Tag'

    name = fields.Char(string='Tag', required=True)
    color = fields.Integer(string='Color')
    active = fields.Boolean(string='Active', default=True)
