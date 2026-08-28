# -*- coding: utf-8 -*-
from odoo import fields, models


class HrVersion(models.Model):
    _inherit = 'hr.version'

    # ── Bỏ hạn chế groups (hr.group_hr_user) để nhân viên (public) đều xem được
    #    các field này qua hr.employee (_inherits). CÁC field này ĐÃ được mirror
    #    thành related trên hr.employee.public nên nhân viên thường fetch không lỗi. ──
    sex = fields.Selection(groups=False)
    marital = fields.Selection(groups=False)
    identification_id = fields.Char(groups=False)
    ssnid = fields.Char(groups=False)
    private_street = fields.Char(groups=False)
    private_street2 = fields.Char(groups=False)
    private_city = fields.Char(groups=False)
    private_state_id = fields.Many2one(groups=False)
    private_zip = fields.Char(groups=False)
    private_country_id = fields.Many2one(groups=False)

    def _has_field_access(self, field, operation):
        # CEO có ACL read trên hr.version và cần xem mọi field khi mở tab version
        # (bản ghi hợp đồng). Cấp quyền ĐỌC mọi field cho CEO, tương tự override
        # trên hr.employee. Không dùng groups=False từng field để tránh mở cho
        # nhân viên thường.
        if (operation == 'read' and not self.env.su
                and field.groups != '.'
                and self.env.user.has_group('hr_custom.group_hr_ceo')):
            return True
        return super()._has_field_access(field, operation)
