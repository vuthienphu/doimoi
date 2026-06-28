# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


ACCEPTANCE_TYPE_SELECTION = [
    ('phase', 'Phase Acceptance'),
    ('milestone', 'Milestone Acceptance'),
    ('final', 'Final Acceptance'),
    ('warranty_handover', 'Warranty / Handover'),
]

ACCEPTANCE_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
]


class DcgContractAcceptance(models.Model):
    _name = 'dcg.contract.acceptance'
    _description = 'Contract Acceptance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'acceptance_date desc, id desc'

    name = fields.Char(
        string='Acceptance No.', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True,
        ondelete='restrict', index=True, tracking=True,
    )
    partner_id = fields.Many2one(related='contract_id.partner_id', store=True, string='Customer')
    acceptance_type = fields.Selection(
        selection=ACCEPTANCE_TYPE_SELECTION, string='Acceptance Type',
        required=True, tracking=True,
    )
    acceptance_date = fields.Date(string='Acceptance Date', tracking=True)
    state = fields.Selection(
        selection=ACCEPTANCE_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True,
    )

    # Content
    title = fields.Char(string='Title')
    summary = fields.Html(string='Summary')
    result_note = fields.Html(string='Result Note')
    signed_by_customer = fields.Char(string='Signed By Customer')
    signed_by_company = fields.Char(string='Signed By Company')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dcg_contract_acceptance_attachment_rel',
        'acceptance_id', 'attachment_id', string='Attachments',
    )

    # Links
    payment_id = fields.Many2one(
        'dcg.contract.payment', string='Related Payment',
        domain="[('contract_id', '=', contract_id)]",
    )
    appendix_id = fields.Many2one(
        'dcg.contract.appendix', string='Related Appendix',
        domain="[('contract_id', '=', contract_id)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.contract.acceptance')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({
            'state': 'confirmed',
            'acceptance_date': fields.Date.today(),
        })
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True
