# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Hrlevel(models.Model):
    _name = 'hr.level'
    _description = 'HR Level'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Tên level', required=True, tracking=True)
    number = fields.Char("Số level", required=True, tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            dup = self.search_count([
                ('name', '=', record.name),
                ('id', '!=', record.id),
            ])
            if dup:
                raise ValidationError(_("Tên level này đã tồn tại!"))

    