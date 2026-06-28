# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


REQUIREMENT_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
]


class DcgCrmRequirement(models.Model):
    """Biên bản khảo sát yêu cầu của một opportunity."""
    _name = 'dcg.crm.requirement'
    _description = 'CRM Requirement Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'survey_date desc, id desc'

    # ============================================================
    # Header
    # ============================================================
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        required=True,
        ondelete='cascade',
        index=True,
        domain="[('type', '=', 'opportunity')]",
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='lead_id.partner_id',
        store=True,
        readonly=True,
    )
    survey_date = fields.Date(
        string='Survey Date',
        default=fields.Date.context_today,
        tracking=True,
    )
    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
        default=lambda self: self.env.user,
        tracking=True,
    )
    version = fields.Char(string='Version', default='V1')
    state = fields.Selection(
        selection=REQUIREMENT_STATE_SELECTION,
        string='Status',
        default='draft',
        tracking=True,
    )

    # ============================================================
    # Survey content
    # ============================================================
    current_system = fields.Html(string='Current System')
    pain_point = fields.Html(string='Pain Point')
    business_goal = fields.Html(string='Business Goal')
    scope_summary = fields.Html(string='Scope Summary')
    department_involved = fields.Text(string='Departments Involved')
    input_data_desc = fields.Html(string='Input Data Description')
    output_data_desc = fields.Html(string='Output Data Description')
    integration_requirement = fields.Html(string='Integration Requirement')
    reporting_requirement = fields.Html(string='Reporting Requirement')
    deployment_requirement = fields.Html(string='Deployment Requirement')
    note = fields.Html(string='Note')

    # ============================================================
    # Evidence
    # ============================================================
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'dcg_crm_requirement_attachment_rel',
        'requirement_id',
        'attachment_id',
        string='Attachments',
    )
    meeting_note = fields.Html(string='Meeting Note')
    contact_person_ids = fields.Many2many(
        'res.partner',
        'dcg_crm_requirement_contact_rel',
        'requirement_id',
        'partner_id',
        string='Customer Contacts',
        help='Contact persons from the customer side who participated in the survey.',
    )

    # ============================================================
    # ORM
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('dcg.crm.requirement')
                vals['name'] = seq or _('New')
        return super().create(vals_list)

    # ============================================================
    # Actions
    # ============================================================
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_update_lead_summary(self):
        """Đẩy nội dung khảo sát lên lead (không overwrite mù field đã có dữ liệu)."""
        for rec in self:
            lead = rec.lead_id
            vals = {}
            if rec.pain_point and not lead.pain_point:
                vals['pain_point'] = rec.pain_point
            if rec.business_goal and not lead.business_goal:
                vals['business_goal'] = rec.business_goal
            if rec.current_system and not lead.current_system:
                vals['current_system'] = rec.current_system
            if vals:
                lead.write(vals)
        return True
