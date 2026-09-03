# -*- coding: utf-8 -*-
from odoo import api, models


class HrVersion(models.Model):
    _inherit = 'hr.version'

    @api.depends('job_id', 'job_id.name',
                 'employee_id.level_id', 'employee_id.level_id.name')
    def _compute_job_title(self):
        """Chức danh = Level + Vị trí công việc, ví dụ 'Middle Developer'.

        Nếu thiếu một trong hai thì lấy tên còn lại; thiếu cả hai thì để trống.
        Ghi đè compute lõi (vốn chỉ lấy tên vị trí công việc).
        """
        for version in self:
            level = version.employee_id.level_id.name
            job = version.job_id.name
            parts = [part for part in (level, job) if part]
            version.job_title = ' '.join(parts) if parts else False
