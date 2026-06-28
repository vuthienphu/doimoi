# -*- coding: utf-8 -*-
from odoo import fields, models


MEMBER_ROLE_SELECTION = [
    ('pm', 'Project Manager'),
    ('ba', 'Business Analyst'),
    ('dev', 'Developer'),
    ('qa', 'QA / Tester'),
    ('consultant', 'Consultant'),
    ('trainer', 'Trainer'),
    ('support', 'Support'),
    ('other', 'Other'),
]


class DcgProjectMember(models.Model):
    _name = 'dcg.project.member'
    _description = 'Project Member'
    _order = 'role, id'

    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True,
    )
    user_id = fields.Many2one(
        'res.users', string='User', required=True,
        domain="[('share', '=', False)]",
    )
    employee_id = fields.Many2one('hr.employee', string='Employee')
    role = fields.Selection(
        selection=MEMBER_ROLE_SELECTION, string='Role',
        required=True, default='dev',
    )
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    allocation_percent = fields.Float(
        string='Allocation (%)', default=100.0,
        help='100 = full-time on this project.',
    )
    is_billable = fields.Boolean(string='Billable', default=True)
    note = fields.Text(string='Note')
