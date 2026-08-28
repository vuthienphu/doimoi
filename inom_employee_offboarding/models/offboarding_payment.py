# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InomOffboardingPaymentTemplate(models.Model):
    _name = 'inom.offboarding.payment.template'
    _description = 'Offboarding Payment Template'
    _order = 'sequence, id'

    name = fields.Char('Khoản', required=True, translate=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    notes = fields.Text(string='Ghi chú')
    append_last_day = fields.Boolean(string='Thêm Last Working Day dự kiến vào cuối tên')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Công ty',
        default=lambda self: self.env.company,
    )

    @api.constrains('sequence')
    def _check_sequence(self):
        for rec in self:
            if rec.sequence < 0:
                raise ValidationError(_('Thứ tự không được là số âm.'))


class InomOffboardingPaymentLine(models.Model):
    _name = 'inom.offboarding.payment.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Offboarding Payment Line'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        comodel_name='inom.offboarding.request',
        string='Yêu cầu nghỉ việc',
        required=True,
        tracking=True,
        ondelete='cascade',
    )
    template_id = fields.Many2one(
        comodel_name='inom.offboarding.payment.template',
        string='Mẫu',
        tracking=True,
    )
    name = fields.Char(string='Khoản', required=True, translate=True, tracking=True)
    sequence = fields.Integer(string='Thứ tự', default=10, tracking=True)
    is_paid = fields.Boolean(string='Trạng thái thanh toán', tracking=True)
    notes = fields.Text(string='Ghi chú', tracking=True)

    def unlink(self):
        for rec in self:
            if rec.request_id.state in ('approved', 'relieved'):
                raise ValidationError(_('Không thể xóa khoản thanh toán khi đơn đã được HRM duyệt.'))
        return super().unlink()



