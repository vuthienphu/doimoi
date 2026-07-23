# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLeadCostRequest(models.Model):
    _name = 'crm.lead.cost.request'
    _description = 'Yêu cầu duyệt chi phí'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Nội dung chi phí', required=True, tracking=True)
    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, tracking=True, domain="[('type', '=', 'opportunity')]")
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
        tracking=True,
    )
    date = fields.Date(string='Ngày chi', default=fields.Date.context_today, required=True, tracking=True)
    amount = fields.Monetary(string='Số tiền', required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='lead_id.currency_id',
        store=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Người yêu cầu',
        default=lambda self: self.env.user,
        required=True,
        readonly=True,
        tracking=True,
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Quản lý duyệt',
        required=True,
        tracking=True,
        domain=lambda self: [('group_ids', 'in', self.env.ref('dcg_crm_payment.group_crm_payment_manager').id)],
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'crm_lead_cost_request_attachment_rel',
        'request_id',
        'attachment_id',
        string='Chứng từ đính kèm',
    )
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('submitted', 'Chờ duyệt'),
            ('approved', 'Đã duyệt'),
            ('rejected', 'Từ chối'),
        ],
        string='Trạng thái',
        default='draft',
        required=True,
        tracking=True,
    )

    def action_submit(self):
        self.ensure_one()
        self.write({'state': 'submitted'})
        self._send_approval_request_email()

    def action_approve(self):
        self.ensure_one()
        if not self.env.user.has_group('dcg_crm_payment.group_crm_payment_manager'):
            raise UserError("Chỉ Quản lý thanh toán mới có quyền phê duyệt yêu cầu này!")

        cost_vals = {
            'lead_id': self.lead_id.id,
            'cost_type': self.cost_type,
            'name': self.name,
            'date': self.date,
            'amount': self.amount,
            'user_id': self.user_id.id,
            'attachment_ids': [(6, 0, self.attachment_ids.ids)] if self.attachment_ids else False,
        }
        # Tạo chi phí trực tiếp trên lead bằng cách bypass check quyền trong crm.lead.cost
        self.env['crm.lead.cost'].with_context(bypass_payment_manager_check=True).create(cost_vals)

        self.write({'state': 'approved'})

    def action_reject(self):
        self.ensure_one()
        if not self.env.user.has_group('dcg_crm_payment.group_crm_payment_manager'):
            raise UserError("Chỉ Quản lý thanh toán mới có quyền từ chối yêu cầu này!")
        self.write({'state': 'rejected'})

    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def _send_approval_request_email(self):
        self.ensure_one()
        template = self.env.ref('dcg_crm_payment.mail_template_cost_approval', raise_if_not_found=False)
        if template:
            template.send_mail(
                self.id,
                force_send=True,
                email_values={'email_to': self.manager_id.email},
            )
