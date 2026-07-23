# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLeadWorkEstimation(models.Model):
    _name = 'crm.lead.work.estimation'
    _description = 'Ước tính công việc cơ hội'
    _order = 'module, id'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, ondelete='cascade')
    module = fields.Char(string='Module', required=True)
    name = fields.Char(string='Chức năng', required=True)
    description = fields.Text(string='Mô tả chức năng')
    priority = fields.Selection(
        [
            ('low', 'Thấp'),
            ('medium', 'Trung bình'),
            ('high', 'Cao'),
        ],
        string='Độ ưu tiên',
        default='medium',
        required=True,
    )
    ba_md = fields.Float(string='BA (MD)', default=0.0)
    backend_md = fields.Float(string='Backend (MD)', default=0.0)
    frontend_md = fields.Float(string='Frontend (MD)', default=0.0)
    qa_md = fields.Float(string='QA (MD)', default=0.0)
    devops_md = fields.Float(string='DevOps (MD)', default=0.0)
    uiux_md = fields.Float(string='UI/UX (MD)', default=0.0)
    total_md = fields.Float(string='Tổng MD', compute='_compute_total_md', store=True)

    @api.depends('ba_md', 'backend_md', 'frontend_md', 'qa_md', 'devops_md', 'uiux_md')
    def _compute_total_md(self):
        for record in self:
            record.total_md = (
                record.ba_md +
                record.backend_md +
                record.frontend_md +
                record.qa_md +
                record.devops_md +
                record.uiux_md
            )

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
