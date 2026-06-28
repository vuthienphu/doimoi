# -*- coding: utf-8 -*-
from odoo import fields, models


SKILL_LEVEL_SELECTION = [
    ('1', '1 - Beginner'),
    ('2', '2 - Basic'),
    ('3', '3 - Intermediate'),
    ('4', '4 - Advanced'),
    ('5', '5 - Expert'),
]

SKILL_CATEGORY_SELECTION = [
    ('technical', 'Technical'),
    ('functional', 'Functional'),
    ('domain', 'Domain'),
    ('tool', 'Tool'),
    ('soft', 'Soft Skill'),
    ('other', 'Other'),
]


class DcgResourceSkill(models.Model):
    _name = 'dcg.resource.skill'
    _description = 'Resource Skill'
    _order = 'employee_id, skill_name'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', index=True,
    )
    skill_name = fields.Char(string='Skill', required=True)
    skill_category = fields.Selection(
        selection=SKILL_CATEGORY_SELECTION, string='Category', default='technical',
    )
    level = fields.Selection(
        selection=SKILL_LEVEL_SELECTION, string='Level', default='3',
    )
    years_of_experience = fields.Float(string='Experience (years)')
    certified = fields.Boolean(string='Certified')
    last_used_date = fields.Date(string='Last Used')
    note = fields.Text(string='Note')
