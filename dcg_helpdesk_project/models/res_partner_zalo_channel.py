from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerZaloChannel(models.Model):
    _name = 'res.partner.zalo.channel'
    _description = 'Kênh Zalo'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Công ty',
        required=False,
        ondelete='set null',
        domain="[('is_company', '=', True)]",
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Dự án mặc định',
        required=False,
        ondelete='set null',
        domain="[('partner_id', '=', partner_id)]",
        help='Dự án mặc định sẽ tự động gán cho các Ticket đến từ kênh Zalo này.',
    )
    name = fields.Char(string='Tên kênh', required=True)
    channel_id = fields.Char(string='ID Kênh Zalo', required=True, index=True)
    active = fields.Boolean(string='Kích hoạt', default=True)

    mapping_status = fields.Selection(
        [
            ('unmapped', 'Partner chưa xác định'),
            ('mapped', 'Đã có Partner'),
        ],
        string='Trạng thái liên kết',
        compute='_compute_mapping_status',
        store=True,
        group_expand='_read_group_mapping_status',
    )

    @api.constrains('channel_id')
    def _check_channel_id_uniq(self):
        for record in self:
            if record.channel_id:
                domain = [('channel_id', '=', record.channel_id), ('id', '!=', record.id)]
                if self.search_count(domain):
                    raise ValidationError(_('ID Kênh Zalo phải là duy nhất!'))

    @api.depends('partner_id')
    def _compute_mapping_status(self):
        for record in self:
            record.mapping_status = 'mapped' if record.partner_id else 'unmapped'

    @api.model
    def _read_group_mapping_status(self, statuses, domain):
        return ['unmapped', 'mapped']

    def write(self, vals):
        res = super().write(vals)
        if 'partner_id' in vals or 'project_id' in vals:
            for record in self:
                tickets = self.env['helpdesk.ticket'].search([
                    '|',
                    ('zalo_channel_id', '=', record.id),
                    ('external_partner_id', '=', record.channel_id),
                ])
                if tickets:
                    update_data = {}
                    if 'partner_id' in vals:
                        update_data['partner_id'] = record.partner_id.id if record.partner_id else False
                        update_data['zalo_channel_id'] = record.id
                    if update_data:
                        tickets.write(update_data)

                    if 'project_id' in vals and record.project_id:
                        unprojected_tickets = tickets.filtered(lambda t: not t.project_id)
                        if unprojected_tickets:
                            unprojected_tickets.write({'project_id': record.project_id.id})
        return res

