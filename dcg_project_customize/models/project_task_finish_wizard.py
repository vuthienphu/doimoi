# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProjectTaskFinishWizard(models.TransientModel):
    _name = 'project.task.finish.wizard'
    _description = 'Nhập lý do quá hạn khi kết thúc Task'

    task_id = fields.Many2one('project.task', string='Công việc', required=True)
    over_deadline_reason = fields.Text(string='Lý do quá hạn', required=True)

    def action_confirm_finish(self):
        self.ensure_one()
        if not self.over_deadline_reason.strip():
            raise ValidationError('Bạn bắt buộc phải nhập lý do quá hạn.')
            
        self.task_id.write({'over_deadline_reason': self.over_deadline_reason})
        
        self.task_id.action_timer_pause()
        done_stage = self.env['project.task.type'].search([('is_done', '=', True)], limit=1)
        if done_stage:
            self.task_id.write({'stage_id': done_stage.id})
