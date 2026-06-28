# -*- coding: utf-8 -*-
from odoo import fields, models

class DcgAssetSoftwareInstall(models.Model):
    _name = 'dcg.asset.software.install'
    _description = 'Asset Software Install'
    _order = 'install_date desc'

    asset_id = fields.Many2one('dcg.asset', string='Device', required=True, ondelete='cascade', index=True)
    software_name = fields.Char(string='Software', required=True)
    version = fields.Char(string='Version')
    install_date = fields.Date(string='Install Date', default=fields.Date.context_today)
    license_id = fields.Many2one('dcg.asset.license', string='License')
    installed_by_id = fields.Many2one('res.users', string='Installed By', default=lambda self: self.env.user)
    note = fields.Text(string='Note')
