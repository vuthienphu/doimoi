# -*- coding: utf-8 -*-
import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DcgAlertRule(models.Model):
    _name = 'dcg.alert.rule'
    _description = 'Alert Rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Rule Name',
        required=True,
        tracking=True,
        translate=True,
    )
    rule_type = fields.Selection(
        selection=[
            ('overdue_receivable', 'Overdue Receivable'),
            ('timesheet_missing', 'Timesheet Missing'),
            ('sla_breach', 'SLA Breach'),
            ('project_overdue', 'Project Overdue'),
            ('task_overdue', 'Task Overdue'),
            ('resource_overload', 'Resource Overload'),
            ('low_margin', 'Low Margin'),
            ('other', 'Other'),
        ],
        string='Rule Type',
        required=True,
        tracking=True,
    )
    model_name = fields.Char(
        string='Target Model',
        help='Technical name of the Odoo model that the rule applies to (e.g., account.move, project.task).',
    )
    condition_json = fields.Text(
        string='Condition (JSON)',
        help='Rule condition stored as JSON, e.g.: {"days_overdue": 7, "amount_gt": 10000000}',
    )
    recipient_group_ids = fields.Many2many(
        'res.groups',
        string='Recipient Groups',
        help='User groups that will receive this alert.',
    )
    active = fields.Boolean(default=True, tracking=True)
    note = fields.Text(string='Internal Note', translate=True)

    @api.constrains('condition_json')
    def _check_condition_json(self):
        for rec in self:
            if rec.condition_json:
                try:
                    json.loads(rec.condition_json)
                except (ValueError, TypeError):
                    raise ValidationError(_(
                        "The Condition field must contain valid JSON."
                    ))
