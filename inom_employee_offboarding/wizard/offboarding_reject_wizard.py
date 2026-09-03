# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class InomOffboardingRejectWizard(models.TransientModel):
    _name = 'inom.offboarding.reject.wizard'
    _description = 'Offboarding Request Rejection Wizard'

    request_id = fields.Many2one(
        comodel_name='inom.offboarding.request',
        string='Offboarding Request',
        required=True,
        ondelete='cascade',
    )
    rejection_reason = fields.Text(
        string='Lý do từ chối',
        required=True,
    )

    def action_confirm_reject(self):
        self.ensure_one()
        request = self.request_id
        if request.state in ('relieved', 'rejected'):
            raise UserError(_(
                'Bản ghi này đã được cập nhật. Vui lòng làm mới trang.'))
        request.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })
        request.message_post(
            body=_('Request rejected. Reason: %s') % self.rejection_reason)
        context = {'record_url': request._get_record_url()}
        request._send_offboarding_mail(
            'inom_employee_offboarding.mail_template_offboarding_rejected',
            request.employee_id.work_email,
            context)
        return {'type': 'ir.actions.act_window_close'}