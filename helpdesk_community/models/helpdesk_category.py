from odoo import fields, models


class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Helpdesk Category'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    team_id = fields.Many2one('helpdesk.team', string='Default Team')
    color = fields.Integer(string='Color')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
