# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


REQUESTED_BY_SELECTION = [
    ('customer', 'Customer'),
    ('internal', 'Internal'),
]

CR_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('analysis', 'Impact Analysis'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('implemented', 'Implemented'),
    ('cancelled', 'Cancelled'),
]


class DcgProjectChangeRequest(models.Model):
    _name = 'dcg.project.change.request'
    _description = 'Project Change Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    # Links
    project_id = fields.Many2one(
        'dcg.project.delivery', string='Project', required=True,
        ondelete='cascade', index=True,
    )
    contract_id = fields.Many2one(
        'dcg.contract', string='Contract', required=True,
    )
    scope_id = fields.Many2one(
        'dcg.project.scope', string='Scope',
        domain="[('project_id', '=', project_id)]",
    )
    appendix_id = fields.Many2one(
        'dcg.contract.appendix', string='Generated Appendix', readonly=True, copy=False,
    )

    # Identification
    name = fields.Char(
        string='CR Number', required=True, copy=False,
        default=lambda self: _('New'), tracking=True,
    )
    request_date = fields.Date(
        string='Request Date', default=fields.Date.context_today, tracking=True,
    )
    requested_by = fields.Selection(
        selection=REQUESTED_BY_SELECTION, string='Requested By',
        required=True, default='customer',
    )
    owner_id = fields.Many2one(
        'res.users', string='Owner', default=lambda self: self.env.user, tracking=True,
    )
    state = fields.Selection(
        selection=CR_STATE_SELECTION, string='Status',
        default='draft', required=True, tracking=True,
    )

    # Impact analysis
    description = fields.Html(string='Description')
    impact_scope = fields.Html(string='Scope Impact')
    impact_timeline = fields.Html(string='Timeline Impact')
    impact_cost = fields.Html(string='Cost Impact')
    decision_note = fields.Html(string='Decision Note')

    # Estimates
    currency_id = fields.Many2one(
        related='contract_id.currency_id', string='Currency', readonly=True,
    )
    estimated_extra_hours = fields.Float(string='Extra Hours')
    estimated_extra_cost = fields.Monetary(string='Extra Cost', currency_field='currency_id')
    estimated_value_delta = fields.Monetary(string='Value Delta', currency_field='currency_id')
    new_target_end_date = fields.Date(string='New Target End Date')

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.project.change.request')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    # ============================================================
    # State actions
    # ============================================================
    def action_submit_analysis(self):
        self.write({'state': 'analysis'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_mark_implemented(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Change request must be approved before marking as implemented."))
            rec.write({'state': 'implemented'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    # ============================================================
    # Create appendix from approved CR
    # ============================================================
    def action_create_appendix(self):
        """Tạo contract appendix từ CR đã approved (spec mục 49)."""
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Change request must be approved before creating an appendix."))
        if self.appendix_id:
            raise UserError(_("An appendix has already been created for this change request."))

        appendix = self.env['dcg.contract.appendix'].create({
            'contract_id': self.contract_id.id,
            'appendix_type': 'scope_change',
            'value_delta': self.estimated_value_delta or 0.0,
            'old_amount_total': self.contract_id.amount_total,
            'old_end_date': self.contract_id.end_date,
            'new_end_date': self.new_target_end_date or False,
            'reason': self.description,
            'summary': _('Generated from Change Request %s') % self.name,
        })
        self.write({'appendix_id': appendix.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.contract.appendix',
            'res_id': appendix.id,
            'view_mode': 'form',
            'target': 'current',
        }
