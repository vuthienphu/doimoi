# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    level_id = fields.Many2one('hr.level', string='Level', groups="hr.group_hr_user")
    

    