# -*- coding: utf-8 -*-
from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count',
                                   groups="om_om_hr_payroll.group_hr_payroll_user")
    struct_id = fields.Many2one(
        related="current_version_id.struct_id",
        string='Salary Structure',
        store=True,
        readonly=False
    )
    identification_issue_date = fields.Date(string='Ngày cấp CCCD')
    identification_issue_place = fields.Char(string='Nơi cấp CCCD')
    identification_expiry_date = fields.Date(string='Ngày hết hạn CCCD')
    passport_issue_date = fields.Date(string='Ngày cấp hộ chiếu')
    passport_expiry_date = fields.Date(string='Ngày hết hạn hộ chiếu')
    labor_contract_ids = fields.Many2many(
        'ir.attachment',
        'hr_employee_labor_contract_rel',
        'employee_id',
        'attachment_id',
        string='Hợp đồng lao động'
    )
    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)
