# -*- coding: utf-8 -*-
from odoo import fields, models


class HrHospital(models.Model):
    _name = 'hr.hospital'
    _description = 'Bệnh viện đăng ký khám chữa bệnh'
    _order = 'name'

    name = fields.Char('Tên bệnh viện', required=True)
    active = fields.Boolean(default=True)
