# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadPayment(models.Model):
    _name = 'crm.lead.payment'
    _description = 'Chi tiết thanh toán cơ hội'
    _order = 'payment_date desc, due_date desc, id desc'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', required=True, ondelete='cascade')
    payment_date = fields.Date(string='Thời gian thanh toán', required=False)
    expected_amount = fields.Monetary(string='Giá trị phải thanh toán', required=True, currency_field='currency_id')
    paid_amount = fields.Monetary(string='Giá trị thanh toán', default=0.0, required=True, currency_field='currency_id')
    due_date = fields.Date(string='Ngày đến hạn', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='lead_id.currency_id',
        store=True,
        readonly=True,
    )
    reminder_sent = fields.Boolean(string='Đã gửi nhắc nhở', default=False)
    
    is_underpaid = fields.Boolean(
        string='Chưa thanh toán đủ',
        compute='_compute_is_underpaid',
        search='_search_is_underpaid',
    )
    is_overdue = fields.Boolean(
        string='Đã quá hạn',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )

    @api.depends('paid_amount', 'expected_amount')
    def _compute_is_underpaid(self):
        for record in self:
            record.is_underpaid = record.paid_amount < record.expected_amount

    @api.depends('paid_amount', 'expected_amount', 'due_date')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.is_overdue = record.paid_amount < record.expected_amount and record.due_date and record.due_date < today

    def _search_is_underpaid(self, operator, value):
        if operator == '=':
            condition = '<' if value else '>='
        elif operator == '!=':
            condition = '>=' if value else '<'
        else:
            condition = '<'
            
        self.env.cr.execute(f"SELECT id FROM crm_lead_payment WHERE paid_amount {condition} expected_amount")
        res = self.env.cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]

    def _search_is_overdue(self, operator, value):
        today = fields.Date.context_today(self)
        if operator == '=':
            if value:
                self.env.cr.execute("SELECT id FROM crm_lead_payment WHERE paid_amount < expected_amount AND due_date < %s", (today,))
            else:
                self.env.cr.execute("SELECT id FROM crm_lead_payment WHERE paid_amount >= expected_amount OR due_date >= %s OR due_date IS NULL", (today,))
        elif operator == '!=':
            if value:
                self.env.cr.execute("SELECT id FROM crm_lead_payment WHERE paid_amount >= expected_amount OR due_date >= %s OR due_date IS NULL", (today,))
            else:
                self.env.cr.execute("SELECT id FROM crm_lead_payment WHERE paid_amount < expected_amount AND due_date < %s", (today,))
                
        res = self.env.cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]

    @api.onchange('paid_amount')
    def _onchange_paid_amount(self):
        if self.paid_amount > 0 and not self.payment_date:
            self.payment_date = fields.Date.context_today(self)
