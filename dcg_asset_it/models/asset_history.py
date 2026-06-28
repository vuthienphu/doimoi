# -*- coding: utf-8 -*-
from odoo import fields, models

HISTORY_ACTION = [
    ('register', 'Registered'),
    ('assign', 'Assigned'),
    ('return', 'Returned'),
    ('transfer', 'Transferred'),
    ('maintenance', 'Maintenance'),
    ('repair', 'Repair'),
    ('warranty_claim', 'Warranty Claim'),
    ('retire', 'Retired'),
    ('dispose', 'Disposed'),
    ('other', 'Other'),
]

class DcgAssetHistory(models.Model):
    _name = 'dcg.asset.history'
    _description = 'Asset History'
    _order = 'action_date desc'

    asset_id = fields.Many2one('dcg.asset', string='Asset', required=True, ondelete='cascade', index=True)
    action = fields.Selection(selection=HISTORY_ACTION, string='Action', required=True)
    action_date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='By', default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    description = fields.Text(string='Description')
