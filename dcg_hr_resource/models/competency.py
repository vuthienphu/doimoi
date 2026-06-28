# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DcgEmployeeCompetency(models.Model):
    _name = 'dcg.employee.competency'
    _description = 'Employee Competency Assessment'
    _order = 'assessment_date desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', index=True,
    )
    period = fields.Char(string='Period', required=True,
        help='e.g. Q2/2026, H1/2026')
    assessment_date = fields.Date(
        string='Assessment Date', default=fields.Date.context_today,
    )
    reviewer_id = fields.Many2one('res.users', string='Reviewer')

    # Scores (1-10)
    technical_score = fields.Float(string='Technical')
    communication_score = fields.Float(string='Communication')
    leadership_score = fields.Float(string='Leadership')
    problem_solving_score = fields.Float(string='Problem Solving')
    teamwork_score = fields.Float(string='Teamwork')
    overall_score = fields.Float(
        string='Overall', compute='_compute_overall', store=True,
    )
    strength = fields.Text(string='Strengths')
    improvement = fields.Text(string='Areas for Improvement')
    note = fields.Text(string='Note')

    @api.depends('technical_score', 'communication_score', 'leadership_score',
                 'problem_solving_score', 'teamwork_score')
    def _compute_overall(self):
        for rec in self:
            scores = [
                rec.technical_score, rec.communication_score,
                rec.leadership_score, rec.problem_solving_score,
                rec.teamwork_score,
            ]
            valid = [s for s in scores if s > 0]
            rec.overall_score = sum(valid) / len(valid) if valid else 0
