# -*- coding: utf-8 -*-

from odoo import fields, models

class CrmDemoChecklistWizard(models.TransientModel):
    _name = 'crm.demo.checklist.wizard'
    _description = 'Xác nhận Checklist Demo'

    checklist_id = fields.Many2one('crm.demo.checklist', string='Checklist', required=True)
    is_confirmed = fields.Boolean(string='Xác nhận')
    notes = fields.Text(string='Ghi chú / Nội dung kiểm tra')

    def action_confirm(self):
        self.ensure_one()
        self.checklist_id.write({
            'is_confirmed': self.is_confirmed,
            'checker_id': self.env.user.id,
            'notes': self.notes
        })
        return {'type': 'ir.actions.act_window_close'}
