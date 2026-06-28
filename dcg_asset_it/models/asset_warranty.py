# -*- coding: utf-8 -*-
from odoo import api, fields, models

class DcgAssetWarranty(models.Model):
    _name = 'dcg.asset.warranty'
    _description = 'Asset Warranty'
    _order = 'end_date desc'

    asset_id = fields.Many2one('dcg.asset', string='Asset', required=True, ondelete='cascade', index=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    warranty_type = fields.Char(string='Warranty Type')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    is_expired = fields.Boolean(string='Expired', compute='_compute_is_expired', store=True)
    contact = fields.Char(string='Contact')
    note = fields.Text(string='Note')

    @api.depends('end_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = bool(rec.end_date and rec.end_date < today)
