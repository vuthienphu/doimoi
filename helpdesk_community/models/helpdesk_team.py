from odoo import fields, models


class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _description = 'Helpdesk Team'

    name = fields.Char(string='Name', required=True, translate=True)
    member_ids = fields.Many2many('res.users', string='Members')
    assignment_policy = fields.Selection(
        [('manual', 'Manual'), ('round_robin', 'Round Robin'),
         ('least_loaded', 'Least Loaded'), ('random', 'Random')],
        string='Assignment Policy', default='manual')
