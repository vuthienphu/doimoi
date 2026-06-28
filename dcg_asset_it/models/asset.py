# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DcgAsset(models.Model):
    _name = 'dcg.asset'
    _description = 'IT Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name_computed'

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    asset_code = fields.Char(
        string='Asset Code', required=True, copy=False,
        default=lambda self: _('New'),
    )
    display_name_computed = fields.Char(
        compute='_compute_display_name_computed', store=True,
    )
    serial_number = fields.Char(string='Serial Number', tracking=True)
    barcode = fields.Char(string='Barcode')
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    # Classification
    type_id = fields.Many2one('dcg.asset.type', string='Type', tracking=True)
    category_id = fields.Many2one('dcg.asset.category', string='Category')
    stage_id = fields.Many2one(
        'dcg.asset.stage', string='Stage', tracking=True, index=True,
        default=lambda self: self.env['dcg.asset.stage'].search(
            [('is_start', '=', True)], limit=1,
        ),
        group_expand='_read_group_stage_ids',
    )
    location_id = fields.Many2one('dcg.asset.location', string='Location')

    # Tech specs
    manufacturer = fields.Char(string='Manufacturer')
    brand = fields.Char(string='Brand')
    model_name = fields.Char(string='Model')
    cpu = fields.Char(string='CPU')
    ram = fields.Char(string='RAM')
    storage = fields.Char(string='Storage')
    mac_address = fields.Char(string='MAC Address')
    ip_address = fields.Char(string='IP Address')
    operating_system = fields.Char(string='OS')

    # Purchase
    purchase_date = fields.Date(string='Purchase Date')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    purchase_price = fields.Monetary(string='Purchase Price', currency_field='currency_id')
    currency_id = fields.Many2one(
        related='company_id.currency_id', store=True,
    )

    # Current assignment
    current_employee_id = fields.Many2one(
        'hr.employee', string='Assigned To',
        compute='_compute_current_assignment', store=True,
    )
    current_project_id = fields.Many2one(
        'dcg.project.delivery', string='Assigned Project',
        compute='_compute_current_assignment', store=True,
    )

    # Relations
    assignment_ids = fields.One2many('dcg.asset.assignment', 'asset_id', string='Assignments')
    history_ids = fields.One2many('dcg.asset.history', 'asset_id', string='History')
    warranty_ids = fields.One2many('dcg.asset.warranty', 'asset_id', string='Warranties')
    maintenance_ids = fields.One2many('dcg.asset.maintenance', 'asset_id', string='Maintenance')
    software_ids = fields.One2many('dcg.asset.software.install', 'asset_id', string='Software')
    checkout_ids = fields.One2many('dcg.asset.checkout', 'asset_id', string='Checkouts')

    note = fields.Html(string='Note')
    image = fields.Image(string='Image', max_width=512, max_height=512)

    @api.depends('name', 'asset_code')
    def _compute_display_name_computed(self):
        for rec in self:
            rec.display_name_computed = '[%s] %s' % (rec.asset_code, rec.name) if rec.asset_code != _('New') else rec.name

    @api.depends('assignment_ids', 'assignment_ids.status')
    def _compute_current_assignment(self):
        for rec in self:
            current = rec.assignment_ids.filtered(lambda a: a.status == 'assigned')[:1]
            rec.current_employee_id = current.employee_id if current else False
            rec.current_project_id = current.project_id if current else False

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['dcg.asset.stage'].search([('active', '=', True)], order='sequence')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('asset_code', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.asset')
                vals['asset_code'] = seq or _('New')
        return super().create(vals_list)
