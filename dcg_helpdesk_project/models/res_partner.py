from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zalo_channel_ids = fields.One2many(
        comodel_name='res.partner.zalo.channel',
        inverse_name='partner_id',
        string='Kênh Zalo',
    )
