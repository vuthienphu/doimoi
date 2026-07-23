# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lesson_ids = fields.Many2many(
        'project.lesson',
        'crm_lead_project_lesson_rel',
        'lead_id',
        'lesson_id',
        string='Bài học kinh nghiệm',
    )
