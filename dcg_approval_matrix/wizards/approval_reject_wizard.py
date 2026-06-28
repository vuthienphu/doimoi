# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class DcgApprovalRejectWizard(models.TransientModel):
    _name = 'dcg.approval.reject.wizard'
    _description = 'Approval Reject Wizard'

    request_id = fields.Many2one(
        'dcg.approval.request',
        string='Request',
        required=True,
        readonly=True,
    )
    reason = fields.Text(
        string='Reject Reason',
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        if not self.reason or not self.reason.strip():
            raise UserError(_("A reason is required to reject an approval request."))
        self.request_id.action_reject(self.reason)
        return {'type': 'ir.actions.act_window_close'}
