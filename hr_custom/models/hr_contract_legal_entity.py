# -*- coding: utf-8 -*-
from odoo import fields, models


class HrContractLegalEntity(models.Model):
    _name = 'hr.contract.legal.entity'
    _description = 'Pháp nhân ký hợp đồng'
    _order = 'name'

    name = fields.Char('Tên pháp nhân', required=True)
    active = fields.Boolean(default=True)
