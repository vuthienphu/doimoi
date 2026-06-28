# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


SCOPE_TYPE_SELECTION = [
    ('implementation', 'Implementation'),
    ('customization', 'Customization'),
    ('integration', 'Integration'),
    ('migration', 'Migration'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('other', 'Other'),
]

SCOPE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('ready', 'Ready'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
]


class DcgProjectScope(models.Model):
    _name = 'dcg.project.scope'
    _description = 'Project Scope / Work Package'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True,
    )
    contract_line_id = fields.Many2one('dcg.contract.line', string='Source Contract Line')
    estimate_line_id = fields.Many2one('dcg.crm.estimate.line', string='Source Estimate Line')
    lead_scope_id = fields.Many2one('dcg.crm.solution.scope', string='Source Presales Scope')

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Work Package', required=True)
    service_catalog_id = fields.Many2one('dcg.service.catalog', string='Service')
    scope_type = fields.Selection(
        selection=SCOPE_TYPE_SELECTION, string='Type', default='implementation',
    )
    description = fields.Html(string='Description')
    owner_id = fields.Many2one('res.users', string='Owner')
    state = fields.Selection(
        selection=SCOPE_STATE_SELECTION, string='Status', default='draft',
    )

    # Timeline / effort
    planned_start_date = fields.Date(string='Planned Start')
    planned_end_date = fields.Date(string='Planned End')
    actual_end_date = fields.Date(string='Actual End')
    planned_hours = fields.Float(string='Planned Hours', compute='_compute_planned_hours', store=True)
    actual_hours = fields.Float(string='Actual Hours')
    progress_percent = fields.Float(string='Progress (%)')
    note = fields.Text(string='Note')

    # Effort snapshot
    ba_hours = fields.Float(string='BA Hours')
    dev_hours = fields.Float(string='Dev Hours')
    test_hours = fields.Float(string='Test Hours')
    pm_hours = fields.Float(string='PM Hours')
    support_hours = fields.Float(string='Support Hours')

    task_ids = fields.One2many('dcg.project.task', 'scope_id', string='Tasks')
    task_count = fields.Integer(compute='_compute_task_count')

    @api.depends('ba_hours', 'dev_hours', 'test_hours', 'pm_hours', 'support_hours')
    def _compute_planned_hours(self):
        for rec in self:
            rec.planned_hours = sum([
                rec.ba_hours or 0, rec.dev_hours or 0, rec.test_hours or 0,
                rec.pm_hours or 0, rec.support_hours or 0,
            ])

    def _compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'res_model': 'dcg.project.task',
            'view_mode': 'kanban,list,form',
            'domain': [('scope_id', '=', self.id)],
            'context': {'default_project_id': self.project_id.id, 'default_scope_id': self.id},
        }
