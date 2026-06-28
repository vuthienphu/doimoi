# -*- coding: utf-8 -*-
from odoo import fields, models


ACTIVITY_TYPE_SELECTION = [
    ('assign', 'Assign'),
    ('comment', 'Comment'),
    ('call', 'Call'),
    ('meeting', 'Meeting'),
    ('deploy', 'Deploy'),
    ('testing', 'Testing'),
    ('customer_reply', 'Customer Reply'),
    ('system', 'System'),
]


class DcgWarrantyActivity(models.Model):
    _name = 'dcg.warranty.activity'
    _description = 'Warranty Ticket Activity'
    _order = 'activity_datetime desc, id desc'

    ticket_id = fields.Many2one(
        'dcg.warranty.ticket', string='Ticket', required=True,
        ondelete='cascade', index=True,
    )
    activity_type = fields.Selection(
        selection=ACTIVITY_TYPE_SELECTION, string='Type',
        required=True, default='comment',
    )
    user_id = fields.Many2one(
        'res.users', string='User', required=True,
        default=lambda self: self.env.user,
    )
    activity_datetime = fields.Datetime(
        string='Date/Time', required=True,
        default=fields.Datetime.now,
    )
    description = fields.Html(string='Description')
    duration_hours = fields.Float(string='Duration (h)')
