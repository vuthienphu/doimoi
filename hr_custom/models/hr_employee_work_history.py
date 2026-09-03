# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployeeWorkHistory(models.Model):
    _name = 'hr.employee.work.history'
    _description = 'Quá trình công tác'
    _order = 'sequence, date_from'

    employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    date_from = fields.Date('Từ ngày', required=True)
    date_to = fields.Date('Đến ngày', required=True)
    job_id = fields.Many2one('hr.job', string='Chức danh', required=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban', required=True)
    level_id = fields.Many2one('hr.level', string='Level', required=True)
    note = fields.Text('Ghi chú')

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_('Từ ngày phải nhỏ hơn hoặc bằng Đến ngày.'))

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_overlap(self):
        for rec in self:
            domain = [
                ('employee_id', '=', rec.employee_id.id),
                ('id', '!=', rec.id),
                ('date_from', '<=', rec.date_to),
                ('date_to', '>=', rec.date_from),
            ]
            if self.search_count(domain):
                raise ValidationError(_('Các khoảng thời gian quá trình công tác không được trùng nhau.'))
