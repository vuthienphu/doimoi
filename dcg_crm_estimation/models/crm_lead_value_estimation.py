# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLeadValueEstimation(models.Model):
    _name = 'crm.lead.value.estimation'
    _description = 'Ước tính giá trị/chi phí khác cơ hội'
    _order = 'cost_type, id'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, ondelete='cascade')
    cost_type = fields.Selection(
        [
            ('license', 'Bản quyền (License)'),
            ('infra', 'Hạ tầng (Infra)'),
            ('partner', 'Đối tác (Partner)'),
            ('travel', 'Công tác (Travel)'),
            ('equipment', 'Thiết bị (Equipment)'),
            ('other', 'Khác (Other)'),
        ],
        string='Loại chi phí',
        default='other',
        required=True,
    )
    name = fields.Char(string='Tên chi phí', required=True)
    quantity = fields.Float(string='Số lượng', default=1.0, required=True)
    unit = fields.Char(string='Đơn vị tính')
    unit_price = fields.Monetary(string='Đơn giá', required=True, currency_field='currency_id')
    subtotal = fields.Monetary(string='Thành tiền', compute='_compute_subtotal', store=True, currency_field='currency_id')
    note = fields.Text(string='Ghi chú')
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='lead_id.currency_id',
        store=True,
        readonly=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.user.has_group('project.group_project_manager') or self.env.user.has_group('base.group_system')):
            raise UserError("Chỉ có Quản lý dự án mới có quyền tạo ước tính!")
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.user.has_group('project.group_project_manager') or self.env.user.has_group('base.group_system')):
            raise UserError("Chỉ có Quản lý dự án mới có quyền chỉnh sửa ước tính!")
        return super().write(vals)

    def unlink(self):
        if not (self.env.user.has_group('project.group_project_manager') or self.env.user.has_group('base.group_system')):
            raise UserError("Chỉ có Quản lý dự án mới có quyền xóa ước tính!")
        return super().unlink()
