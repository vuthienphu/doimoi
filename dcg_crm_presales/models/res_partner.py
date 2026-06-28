# -*- coding: utf-8 -*-
from odoo import api, fields, models


PARTNER_STATUS_SELECTION = [
    ('prospect', 'Prospect'),
    ('active', 'Active Customer'),
    ('inactive', 'Inactive'),
    ('blacklisted', 'Blacklisted'),
]

CUSTOMER_RANK_LEVEL_SELECTION = [
    ('strategic', 'Strategic'),
    ('vip', 'VIP'),
    ('normal', 'Normal'),
    ('low', 'Low'),
]

COOPERATION_STATUS_SELECTION = [
    ('new', 'New'),
    ('negotiating', 'Negotiating'),
    ('active', 'Active'),
    ('on_hold', 'On Hold'),
    ('closed', 'Closed'),
]

DEBT_RISK_LEVEL_SELECTION = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

SUPPORT_LEVEL_SELECTION = [
    ('standard', 'Standard'),
    ('premium', 'Premium'),
    ('vip', 'VIP'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ============================================================
    # Identification
    # ============================================================
    is_company_customer = fields.Boolean(
        string='Target Company Customer',
        help='Marks this partner as a B2B customer account targeted by sales/presales.',
    )
    customer_code = fields.Char(string='Customer Code', index=True)
    account_manager_id = fields.Many2one(
        'res.users',
        string='Account Manager',
        default=lambda self: self.env.user,
        tracking=True,
    )
    partner_status = fields.Selection(
        selection=PARTNER_STATUS_SELECTION,
        string='Customer Status',
        default='prospect',
        tracking=True,
    )

    # ============================================================
    # Classification / master data
    # ============================================================
    dcg_industry_id = fields.Many2one(
        'dcg.customer.industry',
        string='DCG Industry',
        tracking=True,
        help='DCG-specific industry classification (separate from the standard Odoo Industry field).',
    )
    source_id = fields.Many2one(
        'dcg.customer.source',
        string='Source',
        tracking=True,
    )
    customer_rank_level = fields.Selection(
        selection=CUSTOMER_RANK_LEVEL_SELECTION,
        string='Customer Rank',
        default='normal',
    )
    cooperation_status = fields.Selection(
        selection=COOPERATION_STATUS_SELECTION,
        string='Cooperation Status',
        default='new',
    )
    debt_risk_level = fields.Selection(
        selection=DEBT_RISK_LEVEL_SELECTION,
        string='Debt Risk Level',
        default='low',
    )
    support_level = fields.Selection(
        selection=SUPPORT_LEVEL_SELECTION,
        string='Support Level',
        default='standard',
    )

    # ============================================================
    # Internal tracking
    # ============================================================
    note_internal = fields.Text(string='Internal Note')
    last_presales_date = fields.Date(string='Last Presales Date')
    last_contract_date = fields.Date(string='Last Contract Date')

    total_opportunity_count = fields.Integer(
        string='Opportunities',
        compute='_compute_total_opportunity_count',
    )
    total_quotation_count = fields.Integer(
        string='Quotations',
        compute='_compute_total_quotation_count',
    )

    # ============================================================
    # Compute
    # ============================================================
    def _compute_total_opportunity_count(self):
        Lead = self.env['crm.lead']
        for partner in self:
            partner.total_opportunity_count = Lead.search_count([
                ('partner_id', '=', partner.id),
                ('type', '=', 'opportunity'),
            ])

    def _compute_total_quotation_count(self):
        Order = self.env['sale.order']
        for partner in self:
            partner.total_quotation_count = Order.search_count([
                ('partner_id', '=', partner.id),
            ])

    # ============================================================
    # Actions / smart buttons
    # ============================================================
    def action_view_opportunities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Opportunities',
            'res_model': 'crm.lead',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id), ('type', '=', 'opportunity')],
            'context': {'default_partner_id': self.id, 'default_type': 'opportunity'},
        }

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotations',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
