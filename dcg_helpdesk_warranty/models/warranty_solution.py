# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgWarrantySolution(models.Model):
    _name = 'dcg.warranty.solution'
    _description = 'Warranty Solution / Knowledge Base'
    _order = 'create_date desc'

    title = fields.Char(string='Title', required=True)
    problem = fields.Html(string='Problem Description')
    solution = fields.Html(string='Solution')
    module_name = fields.Char(string='Module')
    keyword = fields.Char(string='Keywords')
    tag_ids = fields.Many2many(
        'dcg.warranty.ticket.tag', string='Tags',
    )
    active = fields.Boolean(default=True)
    ticket_count = fields.Integer(
        compute='_compute_ticket_count', string='Tickets',
    )

    def _compute_ticket_count(self):
        Ticket = self.env['dcg.warranty.ticket']
        for rec in self:
            rec.ticket_count = Ticket.search_count(
                [('solution_id', '=', rec.id)]
            ) if rec.id else 0
