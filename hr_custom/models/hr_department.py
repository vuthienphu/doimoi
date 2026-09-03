# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HrDepartment(models.Model):
    _inherit = 'hr.department'
    # đổi tên hiển thị của department từ complete_name sang name
    _rec_name = 'name'

    org_level = fields.Selection([
        ('division', 'Khối'),
        ('department', 'Phòng'),
        ('team', 'Nhóm')
    ], 'Cấp', tracking=True, group_expand='_group_expand_org_level')
    
    hiring_manager_id = fields.Many2one('hr.employee', 'Hiring Manager', 
                                        tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Tài liệu')

    @api.model
    def _group_expand_org_level(self, values, domain):
        # Cố định thứ tự cột khi group by Cấp: Khối -> Phòng -> Nhóm.
        return ['division', 'department', 'team']