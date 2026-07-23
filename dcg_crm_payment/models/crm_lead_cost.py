# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError


class CrmLeadCost(models.Model):
    _inherit = 'crm.lead.cost'

    @api.model_create_multi
    def create(self, vals_list):
        # Nếu không có context bypass_payment_manager_check, kiểm tra quyền Quản lý thanh toán
        if not self.env.context.get('bypass_payment_manager_check'):
            if not self.env.user.has_group('dcg_crm_payment.group_crm_payment_manager'):
                raise UserError("Chỉ có người dùng thuộc nhóm Quản lý thanh toán mới được phép ghi nhận chi phí trực tiếp trên Cơ hội!")
        return super(CrmLeadCost, self).create(vals_list)

    def write(self, vals):
        if not self.env.context.get('bypass_payment_manager_check'):
            if not self.env.user.has_group('dcg_crm_payment.group_crm_payment_manager'):
                raise UserError("Chỉ có người dùng thuộc nhóm Quản lý thanh toán mới được phép chỉnh sửa chi phí!")
        return super(CrmLeadCost, self).write(vals)

    def unlink(self):
        if not self.env.user.has_group('dcg_crm_payment.group_crm_payment_manager'):
            raise UserError("Chỉ có người dùng thuộc nhóm Quản lý thanh toán mới được phép xóa chi phí!")
        return super(CrmLeadCost, self).unlink()
