# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmContract(models.Model):
    _name = 'crm.contract'
    _description = 'Hợp đồng cơ hội'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_signed desc, id desc'

    name = fields.Char(string='Số hợp đồng', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        related='lead_id.partner_id',
        store=True,
        readonly=True,
    )
    lead_id = fields.Many2one('crm.lead', string='Cơ hội', tracking=True)
    project_id = fields.Many2one('project.project', string='Dự án', tracking=True)
    amount = fields.Monetary(
        string='Giá trị hợp đồng',
        related='lead_id.expected_revenue',
        store=True,
        readonly=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='lead_id.currency_id',
        store=True,
        readonly=True,
    )
    date_signed = fields.Date(
        string='Ngày ký',
        default=fields.Date.context_today,
        tracking=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('waiting', 'Chờ ký'),
            ('active', 'Hiệu lực'),
            ('done', 'Hoàn thành'),
            ('cancel', 'Hủy bỏ'),
        ],
        string='Trạng thái',
        default='draft',
        required=True,
        tracking=True,
    )

    def action_waiting(self):
        self.write({'state': 'waiting'})

    def action_active(self):
        self.write({'state': 'active'})
        Project = self.env['project.project']
        for contract in self:
            if contract.lead_id:
                lead = contract.lead_id
                if not lead.project_id:
                    # Tạo dự án cho lead
                    project = Project.create({
                        'name': lead.name,
                        'lead_id': lead.id,
                        'partner_id': lead.partner_id.id,
                        'user_id': lead.user_id.id,
                    })
                    lead.project_id = project.id
                    lead.message_post(
                        body=f"Dự án <b>{project.display_name}</b> đã được tạo tự động từ hợp đồng kích hoạt."
                    )
                # Liên kết chéo hợp đồng và dự án
                project = lead.project_id
                contract.project_id = project.id
                project.contract_id = contract.id

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_view_lead(self):
        self.ensure_one()
        if not self.lead_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cơ hội',
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
