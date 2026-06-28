# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgMasterMixin(models.AbstractModel):
    """Mixin chung cho các model master data đơn giản của DCG."""
    _name = 'dcg.master.mixin'
    _description = 'DCG Master Mixin'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        index=True,
        tracking=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
    )
    note = fields.Text(
        string='Internal Note',
        translate=True,
    )
