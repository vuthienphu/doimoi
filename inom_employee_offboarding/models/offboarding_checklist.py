# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

GROUP_CB = 'inom_employee_offboarding.inom_group_offboarding_officer'
GROUP_HRM = 'inom_employee_offboarding.inom_group_offboarding_hr'
GROUP_CEO = 'inom_employee_offboarding.inom_group_offboarding_ceo'
GROUP_ADMIN = 'inom_employee_offboarding.inom_group_offboarding_admin'
GROUP_HELPDESK = 'inom_employee_offboarding.inom_group_offboarding_helpdesk'


class InomOffboardingChecklistTemplate(models.Model):
    _name = 'inom.offboarding.checklist.template'
    _description = 'Offboarding Checklist Template'
    _order = 'sequence, id'

    name = fields.Char('Task', required=True, translate=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    responsible = fields.Selection([
            ('employee', 'Nhân viên'),
            ('admin', 'Admin'),
            ('helpdesk', 'Helpdesk'),
            ('cnb', 'C&B'),
        ], 'Người phụ trách')
    description = fields.Text(string='Mô tả')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.constrains('sequence')
    def _check_sequence(self):
        for rec in self:
            if rec.sequence < 0:
                raise ValidationError(_('Thứ tự không được là số âm.'))

class InomOffboardingChecklistLine(models.Model):
    _name = 'inom.offboarding.checklist.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Offboarding Checklist Line'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        comodel_name='inom.offboarding.request',
        string='Yêu cầu nghỉ việc',
        required=True,
        tracking=True,
        ondelete='cascade',
    )
    template_id = fields.Many2one(
        comodel_name='inom.offboarding.checklist.template',
        string='Mẫu',
        tracking=True,
    )
    name = fields.Char(string='Task', required=True, translate=True, tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    responsible = fields.Selection([
                ('employee', 'Nhân viên'),
                ('admin', 'Admin'),
                ('helpdesk', 'Helpdesk'),
                ('cnb', 'C&B'),
            ], 'Người phụ trách', tracking=True)
    description = fields.Text(string='Mô tả', tracking=True)
    is_done = fields.Boolean(string='Hoàn thành', tracking=True)
    remarks = fields.Char(string='Ghi chú', tracking=True)

    @api.constrains('is_done')
    def _check_is_done(self):
        user = self.env.user
        is_cb = user.has_group(GROUP_CB)
        is_hrm = user.has_group(GROUP_HRM)
        is_ceo = user.has_group(GROUP_CEO)
        is_admin = user.has_group(GROUP_ADMIN)
        is_helpdesk = user.has_group(GROUP_HELPDESK)

        for rec in self:
            if is_cb and rec.responsible != 'cnb' and rec.is_done == True:
                raise ValidationError(_('C&B chỉ được cập nhật trạng thái dòng checklist của C&B.'))
            if rec.request_id.manager_id == user and rec.responsible == 'employee':
                continue
            if is_hrm or is_ceo:
                raise ValidationError(_('Bạn không có quyền cập nhật trạng thái hoàn thành của checklist.'))
            if is_admin and rec.responsible != 'admin':
                raise ValidationError(_('Admin chỉ được cập nhật trạng thái dòng checklist của Admin.'))
            if is_helpdesk and rec.responsible != 'helpdesk':
                raise ValidationError(_('Helpdesk chỉ được cập nhật trạng thái dòng checklist của Helpdesk.'))