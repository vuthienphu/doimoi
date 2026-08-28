# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class InomOffboardingReason(models.Model):
    _name = 'inom.offboarding.reason'
    _description = 'Employee Offboarding Reason'
    _order = 'sequence, name'

    name = fields.Char(
        string='Tên lý do',
        required=True,
        translate=True,
    )
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Mô tả')
    require_extra_reason = fields.Boolean(string='Bổ sung lý do')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if self.search_count([('name', '=', record.name), ('id', '!=', record.id)]) > 0:
                raise ValidationError("Tên lý do đã tồn tại.")