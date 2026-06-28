# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgContract(models.Model):
    _inherit = 'dcg.contract'

    finance_record_id = fields.Many2one(
        'dcg.project.finance', string='Finance Record',
        compute='_compute_finance_record', store=False,
    )

    def _compute_finance_record(self):
        Finance = self.env['dcg.project.finance']
        for rec in self:
            rec.finance_record_id = Finance.search(
                [('contract_id', '=', rec.id)], limit=1,
            ).id or False
