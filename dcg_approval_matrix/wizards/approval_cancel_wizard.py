# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgApprovalCancelWizard(models.TransientModel):
    _name = 'dcg.approval.cancel.wizard'
    _description = 'Approval Cancel Wizard'

    request_id = fields.Many2one(
        'dcg.approval.request',
        string='Request',
        required=True,
        readonly=True,
    )
    reason = fields.Text(string='Cancel Reason')

    def action_confirm(self):
        self.ensure_one()
        self.request_id.action_cancel(self.reason)
        return {'type': 'ir.actions.act_window_close'}
