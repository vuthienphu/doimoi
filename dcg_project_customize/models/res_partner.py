# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerDepartment(models.Model):
    _name = 'res.partner.department'
    _description = 'Phòng ban công ty khách hàng/nhà cung cấp'
    _order = 'company_id, name'

    name = fields.Char(string='Tên phòng ban', required=True)
    company_id = fields.Many2one(
        'res.partner',
        string='Công ty',
        required=True,
        domain=[('is_company', '=', True)],
        ondelete='cascade',
    )

    _unique_company_name = models.Constraint(
        'UNIQUE(company_id, name)',
        'Phòng ban này đã tồn tại trong công ty.',
    )


class ResPartner(models.Model):
    _inherit = 'res.partner'

    account_user_id = fields.Many2one(
        'res.users',
        string='Tài khoản',
        copy=False,
        domain=[('share', '=', False)],
    )
    partner_department_id = fields.Many2one(
        'res.partner.department',
        string='Phòng ban',
        domain="[('company_id', '=', parent_id)]",
    )
    birthdate = fields.Date(string='Ngày sinh')

    @api.onchange('parent_id')
    def _onchange_parent_id_clear_department(self):
        if self.partner_department_id.company_id != self.parent_id:
            self.partner_department_id = False

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner, vals in zip(partners, vals_list):
            if vals.get('account_user_id'):
                self.env['res.users'].browse(vals['account_user_id']).write({
                    'partner_id': partner.id,
                    'lang': 'vi_VN',
                })
        return partners

    def write(self, vals):
        result = super().write(vals)
        if vals.get('account_user_id'):
            for partner in self:
                self.env['res.users'].browse(vals['account_user_id']).write({
                    'partner_id': partner.id,
                    'lang': 'vi_VN',
                })
        return result
