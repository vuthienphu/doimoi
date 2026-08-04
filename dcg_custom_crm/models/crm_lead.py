# -*- coding: utf-8 -*-

from markupsafe import Markup

from odoo import _, api, fields, models

class CrmDemoChecklist(models.Model):
    _name = 'crm.demo.checklist'
    _description = 'Demo Nội Bộ Checklist'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', ondelete='cascade')
    name = fields.Char(string='Nội dung kiểm tra', required=True)
    checker_id = fields.Many2one('res.users', string='Người kiểm tra')
    is_confirmed = fields.Boolean(string='Xác nhận')
    notes = fields.Text(string='Ghi chú')

    def action_open_confirm_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Xác nhận kiểm tra',
            'res_model': 'crm.demo.checklist.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_checklist_id': self.id,
                'default_is_confirmed': self.is_confirmed,
                'default_notes': self.notes,
            }
        }

class CrmDemoCustomerLine(models.Model):
    _name = 'crm.demo.customer.line'
    _description = 'Chi tiết demo khách hàng'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Demo cho ai')
    feedback = fields.Text(string='Phản hồi khách hàng')
    has_survey_followup = fields.Boolean(string='Phát sinh khảo sát')
    demo_date = fields.Date(string='Ngày demo')

class CrmTag(models.Model):
    _inherit = 'crm.tag'

    module_function = fields.Text(string='Chức năng module')
    checklist_text = fields.Text(string='Checklist kiểm tra')

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    contract_type = fields.Selection([
        ('package', 'Trọn gói'),
        ('service', 'Thuê dịch vụ')
    ], string='Loại hợp đồng', default='package')
    periodic_revenue = fields.Monetary(string='Doanh thu từng kỳ', currency_field='company_currency')

    survey_date = fields.Date(string='Ngày khảo sát')
    surveyor_id = fields.Many2one('res.users', string='Người khảo sát')
    customer_contact_id = fields.Many2one('res.partner', string='Người liên hệ KH')
    dev_requirement_clear = fields.Boolean(string='Rõ yêu cầu Dev (PM tích)')

    internal_demo_checklist_ids = fields.One2many(
        'crm.demo.checklist',
        'lead_id',
        string='Checklist demo nội bộ'
    )
    customer_demo_line_ids = fields.One2many(
        'crm.demo.customer.line',
        'lead_id',
        string='Chi tiết demo khách hàng'
    )

    commission_rate = fields.Float(
        string='Phần trăm hoa hồng (%)',
        compute='_compute_commission_rate',
        store=True,
        readonly=True,
    )
    other_ids = fields.Many2many(
        'res.partner',
        'crm_lead_other_partner_rel',
        'lead_id',
        'partner_id',
        string='Người liên hệ khác',
        domain=[('is_company', '=', False)],
    )
    survey_note = fields.Text(string='Tài liệu')
    estimate_attachment_ids = fields.Many2many(
        'ir.attachment',
        'crm_lead_estimate_attachment_rel',
        'lead_id',
        'attachment_id',
        string='File ước tính công việc',
    )
    survey_done = fields.Boolean(string='Đã khảo sát', default=False)
    survey_finish_date = fields.Datetime(string='Ngày hoàn thành khảo sát', readonly=True)
    survey_line_ids = fields.One2many(
        'crm.lead.survey.line',
        'lead_id',
        string='Chi tiết khảo sát',
    )
    demo_done = fields.Boolean(string='Đã hoàn thành demo', default=False)
    demo_finish_date = fields.Datetime(string='Thời gian demo', readonly=True)
    is_internal_demo_done = fields.Boolean(string='Đã demo nội bộ', default=False)
    internal_demo_user_ids = fields.Many2many(
        'res.users',
        'crm_lead_internal_demo_user_rel',
        'lead_id',
        'user_id',
        string='Nhân sự demo nội bộ',
    )
    demo_reviewer_ids = fields.Many2many(
        'res.users',
        'crm_lead_demo_reviewer_rel',
        'lead_id',
        'user_id',
        string='Người review demo',
    )
    is_customer_demo_done = fields.Boolean(string='Đã demo cho khách hàng', default=False)
    project_id = fields.Many2one('project.project', string='Link dự án', copy=False)

    @api.onchange('partner_id')
    def _onchange_partner_id_for_decision_maker(self):
        # Khi chọn công ty, tự động tìm liên hệ "Người quyết định" để gán email/sđt
        for lead in self:
            if lead.partner_id and lead.partner_id.is_company:
                decision_maker = self.env['res.partner'].search([
                    ('parent_id', '=', lead.partner_id.id),
                    ('is_decision_maker', '=', True)
                ], limit=1)
                if decision_maker:
                    lead.email_from = decision_maker.email
                    lead.phone = decision_maker.phone

    @api.depends(
        'team_id',
        'user_id',
        'team_id.crm_team_member_ids.active',
        'team_id.crm_team_member_ids.commission_rate',
        'team_id.crm_team_member_ids.user_id',
    )
    def _compute_commission_rate(self):
        TeamMember = self.env['crm.team.member']
        for lead in self:
            member = TeamMember.search([
                ('crm_team_id', '=', lead.team_id.id),
                ('user_id', '=', lead.user_id.id),
                ('active', '=', True),
            ], limit=1)
            lead.commission_rate = member.commission_rate if member else 0.0

    def action_complete_survey(self):
        now = fields.Datetime.now()
        for lead in self:
            lead.write({
                'survey_done': True,
                'survey_finish_date': now,
            })
            lead.message_post(body=_('Đã hoàn thành khảo sát ngày %s.') % fields.Datetime.to_string(now))
            lead._create_project_for_won_opportunities(force_create=True)
        return True

    def action_continue_survey(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tiếp tục khảo sát'),
            'res_model': 'crm.lead.survey.line',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
            },
        }

    def action_complete_demo(self):
        now = fields.Datetime.now()
        for lead in self:
            lead.write({
                'demo_done': True,
                'demo_finish_date': now,
            })
            lead.message_post(body=_('Đã hoàn thành demo ngày %s.') % fields.Datetime.to_string(now))
        return True

    def action_continue_demo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tiếp tục demo'),
            'res_model': 'crm.demo.customer.line',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
            },
        }

    def write(self, vals):
        result = super().write(vals)
        if {'stage_id', 'probability'} & set(vals):
            self._create_project_for_won_opportunities()
        return result

    def action_set_won(self):
        result = super().action_set_won()
        self._create_project_for_won_opportunities()
        return result

    def action_set_won_rainbowman(self):
        result = super().action_set_won_rainbowman()
        self._create_project_for_won_opportunities()
        return result

    def _create_project_for_won_opportunities(self, force_create=False):
        Project = self.env['project.project']
        if force_create:
            won_leads = self.filtered(lambda lead: not lead.project_id)
        else:
            won_leads = self.filtered(
                lambda lead: lead.type == 'opportunity'
                and not lead.project_id
                and (lead.probability >= 100 or lead.stage_id.is_won)
            )
        for lead in won_leads:
            project_vals = {
                'name': lead.name,
                'partner_id': lead.partner_id.id,
                'user_id': lead.user_id.id,
                'x_lead_id': lead.id,
            }
            # dcg_project_customize provides lead_id. Keep both links in sync
            # when that optional module is installed.
            if 'lead_id' in Project._fields:
                project_vals['lead_id'] = lead.id
            project = Project.create(project_vals)
            lead.project_id = project
            lead.message_post(
                body=Markup(_('Dự án <b>%s</b> đã được tạo liên kết với Cơ hội này.')) % project.display_name
            )
