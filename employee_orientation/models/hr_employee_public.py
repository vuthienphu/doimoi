# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    # Mirror certificates sang hồ sơ nhân viên công khai để nhân viên thường
    # (chỉ đọc được hr.employee.public) không bị lỗi truy cập khi đọc field này.
    # compute_sudo: đọc certificates của hr.employee qua sudo, an toàn.
    certificates = fields.Boolean(
        related='employee_id.certificates', compute_sudo=True, readonly=True)
