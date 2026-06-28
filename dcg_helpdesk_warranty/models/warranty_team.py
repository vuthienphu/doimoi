# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgWarrantyTeam(models.Model):
    _name = 'dcg.warranty.team'
    _description = 'Warranty Support Team'
    _order = 'name'

    name = fields.Char(string='Team Name', required=True, translate=True)
    leader_id = fields.Many2one('res.users', string='Team Leader')
    member_ids = fields.Many2many(
        'res.users', 'dcg_warranty_team_member_rel',
        'team_id', 'user_id', string='Members',
    )
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )
