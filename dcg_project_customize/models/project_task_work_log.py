# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta

class ProjectTaskWorkLog(models.Model):
    _name = 'project.task.work.log'
    _description = 'Lịch sử thời gian làm việc trên Task'
    _order = 'start_time desc'

    task_id = fields.Many2one('project.task', string='Công việc', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Người thực hiện', required=True, default=lambda self: self.env.user)
    start_time = fields.Datetime(string='Thời gian bắt đầu', required=True, default=fields.Datetime.now)
    end_time = fields.Datetime(string='Thời gian kết thúc')
    duration = fields.Float(string='Số giờ thực tế', compute='_compute_duration', store=True)
    is_running = fields.Boolean(string='Đang chạy', compute='_compute_is_running', store=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for log in self:
            if log.start_time and log.end_time:
                delta = log.end_time - log.start_time
                log.duration = delta.total_seconds() / 3600.0
            else:
                log.duration = 0.0

    @api.depends('end_time')
    def _compute_is_running(self):
        for log in self:
            log.is_running = not bool(log.end_time)
