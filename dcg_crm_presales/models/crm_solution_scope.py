# -*- coding: utf-8 -*-
from odoo import fields, models


SCOPE_TYPE_SELECTION = [
    ('implementation', 'Implementation'),
    ('customization', 'Customization'),
    ('integration', 'Integration'),
    ('migration', 'Migration'),
    ('training', 'Training'),
    ('support', 'Support'),
    ('consulting', 'Consulting'),
    ('license', 'License'),
    ('other', 'Other'),
]

COMPLEXITY_SELECTION = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]


class DcgCrmSolutionScope(models.Model):
    """Hạng mục giải pháp / scope item đề xuất cho một opportunity."""
    _name = 'dcg.crm.solution.scope'
    _description = 'CRM Solution Scope'
    _order = 'sequence, id'

    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        required=True,
        ondelete='cascade',
        index=True,
        domain="[('type', '=', 'opportunity')]",
    )
    requirement_id = fields.Many2one(
        'dcg.crm.requirement',
        string='Source Requirement',
        domain="[('lead_id', '=', lead_id)]",
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Scope Item', required=True)
    service_catalog_id = fields.Many2one(
        'dcg.service.catalog',
        string='Service',
    )
    scope_type = fields.Selection(
        selection=SCOPE_TYPE_SELECTION,
        string='Scope Type',
        required=True,
        default='implementation',
    )
    description = fields.Html(string='Description')
    in_scope = fields.Boolean(
        string='In Scope',
        default=True,
        help='Unchecking marks this item as proposed but excluded from the final proposal.',
    )
    estimated_complexity = fields.Selection(
        selection=COMPLEXITY_SELECTION,
        string='Complexity',
        default='medium',
    )
    estimated_note = fields.Text(string='Estimate Note')
    active = fields.Boolean(default=True)
