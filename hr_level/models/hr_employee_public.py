# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    # Mirror level_id sang hồ sơ nhân viên công khai để nhân viên thường
    # (chỉ có quyền đọc hr.employee.public) không bị lỗi truy cập.
    # compute_sudo: đọc level_id của hr.employee qua sudo, an toàn.
    level_id = fields.Many2one(
        'hr.level', string='Level',
        related='employee_id.level_id', compute_sudo=True, readonly=True)
