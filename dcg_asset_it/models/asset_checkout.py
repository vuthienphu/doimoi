# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

CHECKOUT_STATE = [
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('checked_out', 'Checked Out'),
    ('returned', 'Returned'),
    ('cancelled', 'Cancelled'),
]

class DcgAssetCheckout(models.Model):
    _name = 'dcg.asset.checkout'
    _description = 'Asset Checkout (Short-term)'
    _inherit = ['mail.thread']
    _order = 'checkout_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Checkout No.', required=True, copy=False, default=lambda self: _('New'))
    asset_id = fields.Many2one('dcg.asset', string='Asset', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Borrower', required=True)
    purpose = fields.Char(string='Purpose', required=True)
    checkout_date = fields.Datetime(string='Checkout', required=True, default=fields.Datetime.now)
    expected_return = fields.Datetime(string='Expected Return', required=True)
    actual_return = fields.Datetime(string='Actual Return')
    state = fields.Selection(selection=CHECKOUT_STATE, string='Status', default='draft', tracking=True)
    approver_id = fields.Many2one('res.users', string='Approver')
    note = fields.Text(string='Note')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.asset.checkout')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def action_approve(self):
        self.write({'state': 'approved', 'approver_id': self.env.uid})

    def action_checkout(self):
        self.write({'state': 'checked_out'})

    def action_return(self):
        self.write({'state': 'returned', 'actual_return': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
