# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='company_id.currency_id',
        readonly=True,
    )
    payment_type_id = fields.Many2one('crm.payment.type', string='Loại thanh toán')
    first_payment_date = fields.Date(string='Ngày thanh toán đầu tiên')
    last_payment_date = fields.Date(
        string='Ngày thanh toán gần nhất',
        compute='_compute_payment_totals',
        store=True,
        readonly=True,
    )
    payment_ids = fields.One2many('crm.lead.payment', 'lead_id', string='Lịch sử thanh toán')
    total_paid = fields.Monetary(
        string='Đã thanh toán',
        compute='_compute_payment_totals',
        store=True,
        currency_field='currency_id',
    )
    remaining_amount = fields.Monetary(
        string='Còn lại',
        compute='_compute_payment_totals',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('payment_ids.paid_amount', 'payment_ids.payment_date', 'expected_revenue')
    def _compute_payment_totals(self):
        for lead in self:
            lead.total_paid = sum(lead.payment_ids.mapped('paid_amount'))
            lead.remaining_amount = lead.expected_revenue - lead.total_paid
            
            payment_dates = lead.payment_ids.filtered(lambda p: p.payment_date).mapped('payment_date')
            lead.last_payment_date = max(payment_dates) if payment_dates else False

    @api.model
    def _cron_send_payment_reminders(self):
        today = fields.Date.context_today(self)
        leads = self.search([
            ('remaining_amount', '>', 0),
            ('payment_type_id', '!=', False),
            ('first_payment_date', '!=', False),
            ('user_id', '!=', False),
        ])
        for lead in leads:
            cycle_days = lead.payment_type_id.cycle_days
            remind_before_days = lead.payment_type_id.remind_before_days
            if cycle_days <= 0:
                continue

            first_date = lead.first_payment_date
            delta = (today - first_date).days
            if delta < 0:
                next_due_date = first_date
            else:
                n = delta // cycle_days
                next_due_date = first_date + timedelta(days=n * cycle_days)
                if next_due_date < today:
                    next_due_date = first_date + timedelta(days=(n + 1) * cycle_days)

            days_to_due = (next_due_date - today).days
            if 0 <= days_to_due <= remind_before_days:
                lead._send_payment_reminder_email(next_due_date)

    def _send_payment_reminder_email(self, next_due_date):
        self.ensure_one()
        template = self.env.ref('dcg_crm_payment.mail_template_payment_reminder', raise_if_not_found=False)
        if template:
            template.with_context(next_due_date=next_due_date).send_mail(
                self.id,
                force_send=True,
                email_values={'email_to': self.user_id.email},
            )
