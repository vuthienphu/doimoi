from odoo import models, fields


class ResPartnerZaloChannel(models.Model):
    _name = 'res.partner.zalo.channel'
    _description = 'Kênh Zalo'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Công ty',
        required=True,
        ondelete='cascade',
        domain="[('is_company', '=', True)]",
    )
    name = fields.Char(string='Tên kênh', required=True)
    channel_id = fields.Char(string='ID Kênh Zalo', required=True, index=True)
    active = fields.Boolean(string='Kích hoạt', default=True)

    _sql_constraints = [
        ('channel_id_uniq', 'unique(channel_id)', 'ID Kênh Zalo phải là duy nhất!'),
    ]
