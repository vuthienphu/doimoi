# -*- coding: utf-8 -*-
from odoo import fields, models


MEMBER_ROLE_SELECTION = [
    ('pm', 'Project Manager'),
    ('ba', 'BA'),
    ('dev', 'Developer'),
    ('qa', 'QA'),
    ('trainer', 'Trainer'),
    ('support', 'Support'),
    ('sales', 'Sales'),
    ('other', 'Other'),
]


class DcgBusinessTripMember(models.Model):
    _name = 'dcg.business.trip.member'
    _description = 'Business Trip Member'
    _order = 'trip_id, id'

    trip_id = fields.Many2one(
        'dcg.business.trip', string='Trip', required=True,
        ondelete='cascade', index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
    )
    user_id = fields.Many2one(
        related='employee_id.user_id', string='User', store=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id', string='Department', store=True,
    )
    role = fields.Selection(
        selection=MEMBER_ROLE_SELECTION, string='Role', default='other',
    )
    is_team_lead = fields.Boolean(string='Team Lead')
    join_datetime = fields.Datetime(string='Join Date')
    leave_datetime = fields.Datetime(string='Leave Date')
    note = fields.Text(string='Note')
