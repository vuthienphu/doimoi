from odoo import fields, models


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _description = 'Helpdesk Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_start = fields.Boolean(string='Start Stage',
                               help='Default stage for new tickets')
    is_done = fields.Boolean(string='Done Stage',
                              help='Terminal stage (closed/resolved)')
    fold = fields.Boolean(string='Folded in Kanban')
    team_ids = fields.Many2many('helpdesk.team', string='Teams')
