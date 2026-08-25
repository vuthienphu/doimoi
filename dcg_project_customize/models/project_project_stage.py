# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'
    description = fields.Text(string='Ý nghĩa')
    checklist_template_ids = fields.One2many(
        'project.stage.checklist.template',
        'stage_id',
        string='Template Checklist Bàn Giao'
    )

    @api.model
    def _dcg_open_all_project_stages(self):
        self.with_context(active_test=False).search([('fold', '=', True)]).write({'fold': False})

class ProjectStageChecklistTemplate(models.Model):
    _name = 'project.stage.checklist.template'
    _description = 'Template Checklist Bàn Giao'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Tên tài liệu', required=True)
    stage_id = fields.Many2one('project.project.stage', string='Trạng thái dự án', ondelete='cascade')
