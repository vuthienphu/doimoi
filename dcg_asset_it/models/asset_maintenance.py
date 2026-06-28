# -*- coding: utf-8 -*-
from odoo import fields, models

class DcgAssetMaintenance(models.Model):
    _name = 'dcg.asset.maintenance'
    _description = 'Asset Maintenance'
    _order = 'maintenance_date desc'

    asset_id = fields.Many2one('dcg.asset', string='Asset', required=True, ondelete='cascade', index=True)
    maintenance_date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    supplier = fields.Char(string='Supplier')
    cost = fields.Monetary(string='Cost', currency_field='currency_id')
    currency_id = fields.Many2one(related='asset_id.currency_id', store=True)
    description = fields.Text(string='Description')
    attachment_ids = fields.Many2many('ir.attachment', 'dcg_asset_maint_attach_rel', 'maint_id', 'attach_id', string='Attachments')
