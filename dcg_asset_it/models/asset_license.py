# -*- coding: utf-8 -*-
from odoo import api, fields, models

class DcgAssetLicense(models.Model):
    _name = 'dcg.asset.license'
    _description = 'Software License'
    _order = 'expiry_date'

    name = fields.Char(string='Software', required=True)
    license_key = fields.Char(string='License Key')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    purchase_date = fields.Date(string='Purchase Date')
    expiry_date = fields.Date(string='Expiry Date')
    is_expired = fields.Boolean(string='Expired', compute='_compute_is_expired', store=True)
    seat_count = fields.Integer(string='Total Seats', default=1)
    assigned_employee_ids = fields.Many2many('hr.employee', string='Assigned To')
    assigned_count = fields.Integer(string='Used Seats', compute='_compute_assigned_count', store=True)
    available_seats = fields.Integer(string='Available', compute='_compute_assigned_count', store=True)
    is_over_licensed = fields.Boolean(string='Over-licensed', compute='_compute_assigned_count', store=True)
    cost = fields.Monetary(string='Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    note = fields.Text(string='Note')
    active = fields.Boolean(default=True)

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = bool(rec.expiry_date and rec.expiry_date < today)

    @api.depends('assigned_employee_ids', 'seat_count')
    def _compute_assigned_count(self):
        for rec in self:
            rec.assigned_count = len(rec.assigned_employee_ids)
            rec.available_seats = max((rec.seat_count or 0) - rec.assigned_count, 0)
            rec.is_over_licensed = rec.assigned_count > (rec.seat_count or 0)
