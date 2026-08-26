# -*- coding: utf-8 -*-

from odoo import fields, models

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', readonly=True)
    identification_issue_date = fields.Date(string='Ngày cấp CCCD', readonly=True)
    identification_issue_place = fields.Char(string='Nơi cấp CCCD', readonly=True)
    identification_expiry_date = fields.Date(string='Ngày hết hạn CCCD', readonly=True)
    passport_issue_date = fields.Date(string='Ngày cấp hộ chiếu', readonly=True)
    passport_expiry_date = fields.Date(string='Ngày hết hạn hộ chiếu', readonly=True)
