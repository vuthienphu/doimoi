# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class DcgContractCloseWizard(models.TransientModel):
    _name = 'dcg.contract.close.wizard'
    _description = 'Close Contract Wizard'

    contract_id = fields.Many2one('dcg.contract', string='Contract', required=True, readonly=True)
    close_note = fields.Text(string='Close Note')

    def action_confirm(self):
        self.ensure_one()
        contract = self.contract_id
        if contract.state != 'done':
            raise UserError(_("Contract must be in 'Completed' state to close."))
        contract.write({
            'state': 'closed',
            'internal_note': (contract.internal_note or '') + '\n--- Close note ---\n' + (self.close_note or ''),
        })
        return {'type': 'ir.actions.act_window_close'}
