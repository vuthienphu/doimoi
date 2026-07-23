# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='company_id.currency_id',
        readonly=True,
    )
    payment_type_id = fields.Many2one('crm.payment.type', string='Loại thanh toán')
    payment_cycle_count = fields.Integer(string='Số kỳ thanh toán', default=1)
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
    contract_id = fields.Many2one('crm.contract', string='Hợp đồng', readonly=True)

    @api.depends('payment_ids.paid_amount', 'payment_ids.payment_date', 'expected_revenue')
    def _compute_payment_totals(self):
        for lead in self:
            lead.total_paid = sum(lead.payment_ids.mapped('paid_amount'))
            lead.remaining_amount = lead.expected_revenue - lead.total_paid
            
            payment_dates = lead.payment_ids.filtered(lambda p: p.payment_date).mapped('payment_date')
            lead.last_payment_date = max(payment_dates) if payment_dates else False

    def _generate_payment_schedule(self):
        self.ensure_one()
        if not self.payment_type_id or self.payment_cycle_count <= 0 or not self.first_payment_date or self.expected_revenue <= 0:
            return
            
        commands = [(5, 0, 0)]  # Xóa các dòng lịch sử cũ nếu có
        cycle_days = self.payment_type_id.cycle_days
        amount_per_cycle = self.expected_revenue / self.payment_cycle_count
        
        company_currency = self.company_id.currency_id or self.currency_id
        if company_currency:
            amount_per_cycle = company_currency.round(amount_per_cycle)
            
        for i in range(self.payment_cycle_count):
            due_date = self.first_payment_date + timedelta(days=i * cycle_days)
            commands.append((0, 0, {
                'due_date': due_date,
                'expected_amount': amount_per_cycle,
                'paid_amount': 0.0,
                'payment_date': False,
            }))
        self.payment_ids = commands

    @api.onchange('payment_type_id', 'payment_cycle_count', 'first_payment_date', 'expected_revenue')
    def _onchange_generate_payment_schedule(self):
        for lead in self:
            if not lead.payment_type_id or lead.payment_cycle_count <= 0 or not lead.first_payment_date or lead.expected_revenue <= 0:
                continue
            # Chỉ sinh tự động khi chưa có bất kỳ đợt thanh toán thực tế nào
            if any(line.paid_amount > 0 for line in lead.payment_ids):
                continue
            lead._generate_payment_schedule()

    def action_generate_payment_schedule(self):
        for lead in self:
            if not lead.payment_type_id or lead.payment_cycle_count <= 0 or not lead.first_payment_date or lead.expected_revenue <= 0:
                raise UserError("Vui lòng điền đầy đủ cấu hình thanh toán và doanh thu dự kiến trước khi sinh lịch!")
            
            if any(line.paid_amount > 0 for line in lead.payment_ids):
                raise UserError("Không thể tạo lại lịch thanh toán vì đã có đợt thanh toán được thực tế hóa (Số tiền thanh toán > 0)!")
                
            lead._generate_payment_schedule()

    def action_create_contract(self):
        self.ensure_one()
        if self.contract_id:
            raise UserError("Cơ hội này đã có hợp đồng!")

        # Nếu đang là Lead (type == 'lead'), chuyển thành Opportunity và reload để hiện tab Thanh toán
        if self.type == 'lead':
            self.write({'type': 'opportunity'})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cơ hội',
                'res_model': 'crm.lead',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # Kiểm tra các trường cần thiết để tạo lịch thanh toán (chỉ kiểm tra khi đã là Opportunity)
        missing_fields = []
        if not self.payment_type_id:
            missing_fields.append("- Loại thanh toán")
        if self.payment_cycle_count <= 0:
            missing_fields.append("- Số kỳ thanh toán (phải lớn hơn 0)")
        if not self.first_payment_date:
            missing_fields.append("- Ngày thanh toán đầu tiên")
        if self.expected_revenue <= 0:
            missing_fields.append("- Doanh thu dự kiến / Giá trị hợp đồng (phải lớn hơn 0)")
            
        if missing_fields:
            raise UserError("Để tạo hợp đồng, vui lòng bổ sung đầy đủ thông tin thanh toán:\n" + "\n".join(missing_fields))
            
        # Tự sinh lịch thanh toán nếu chưa có dòng nào
        if not self.payment_ids:
            self._generate_payment_schedule()
            
        contract_vals = {
            'name': f"HĐ/{self.name}",
            'lead_id': self.id,
            'project_id': self.project_id.id if self.project_id else False,
        }
        contract = self.env['crm.contract'].create(contract_vals)
        self.contract_id = contract.id
        
        # Nếu đã có dự án thì gán hợp đồng cho dự án đó
        if self.project_id:
            self.project_id.contract_id = contract.id
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp đồng',
            'res_model': 'crm.contract',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super(CrmLead, self).create(vals_list)
        for record in records:
            if record.payment_type_id and record.payment_cycle_count > 0 and record.first_payment_date and record.expected_revenue > 0 and not record.payment_ids:
                record._generate_payment_schedule()
        return records

    @api.model
    def _cron_send_payment_reminders(self):
        today = fields.Date.context_today(self)
        payments = self.env['crm.lead.payment'].search([
            ('reminder_sent', '=', False),
            ('due_date', '>=', today),
        ])
        for payment in payments:
            lead = payment.lead_id
            if not lead.payment_type_id or not lead.user_id:
                continue
                
            if payment.paid_amount >= payment.expected_amount:
                continue
                
            remind_before_days = lead.payment_type_id.remind_before_days
            days_to_due = (payment.due_date - today).days
            
            if 0 <= days_to_due <= remind_before_days:
                lead._send_payment_reminder_email(payment.due_date)
                payment.reminder_sent = True

    def _send_payment_reminder_email(self, next_due_date):
        self.ensure_one()
        template = self.env.ref('dcg_crm_payment.mail_template_payment_reminder', raise_if_not_found=False)
        if template:
            template.with_context(next_due_date=next_due_date).send_mail(
                self.id,
                force_send=True,
                email_values={'email_to': self.user_id.email},
            )

    def action_view_contract(self):
        self.ensure_one()
        if not self.contract_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp đồng',
            'res_model': 'crm.contract',
            'res_id': self.contract_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    is_payment_manager = fields.Boolean(
        string='Là quản lý thanh toán',
        compute='_compute_is_payment_manager',
    )

    def _compute_is_payment_manager(self):
        is_mgr = self.env.user.has_group('dcg_crm_payment.group_crm_payment_manager')
        for lead in self:
            lead.is_payment_manager = is_mgr
