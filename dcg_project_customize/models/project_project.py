# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    stage_id = fields.Many2one(
        'project.project.stage',
        string='Trạng thái dự án',
        tracking=True,
        ondelete='set null',
    )

    manager_ids = fields.Many2many(
        'res.users',
        'project_project_manager_users_rel',
        'project_id',
        'user_id',
        string='Phụ trách dự án'
    )
    external_user_ids = fields.Many2many(
        'res.users',
        'project_project_external_users_rel',
        'project_id',
        'user_id',
        string='Khách hàng/Nhà cung cấp được cấp quyền',
        domain=[('share', '=', False)],
    )
    eligible_external_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_eligible_external_user_ids',
        string='Tài khoản ngoài hợp lệ',
    )

    lead_id = fields.Many2one(
        'crm.lead',
        string='Cơ hội',
        readonly=True,
        copy=False,
        ondelete='set null',
    )
    member_ids = fields.Many2many(
        'hr.employee.public',
        'project_project_employee_rel',
        'project_id',
        'employee_id',
        string='Thành viên tham gia'
    )
    handover_checklist_ids = fields.One2many(
        'project.handover.checklist',
        'project_id',
        string='Checklist tài liệu bàn giao'
    )

    survey_id = fields.Many2one('survey.survey', string='Khảo sát GoLive', readonly=True, copy=False)

    @api.depends('partner_id')
    def _compute_eligible_external_user_ids(self):
        Users = self.env['res.users'].sudo()
        for project in self:
            customer = project.partner_id.commercial_partner_id
            project.eligible_external_user_ids = Users.search([
                ('share', '=', False),
                ('partner_id.commercial_partner_id', '=', customer.id),
            ]) if customer else Users.browse()

    def write(self, vals):
        res = super().write(vals)
        if 'stage_id' in vals:
            for project in self:
                if project.stage_id:
                    existing_template_ids = project.handover_checklist_ids.mapped('template_id').ids
                    new_checklists = []
                    for template in project.stage_id.checklist_template_ids:
                        if template.id not in existing_template_ids:
                            new_checklists.append((0, 0, {
                                'name': template.name,
                                'template_id': template.id,
                            }))
                    if new_checklists:
                        project.write({'handover_checklist_ids': new_checklists})

                    golive_stage = self.env.ref(
                        'dcg_project_customize.project_stage_golive', raise_if_not_found=False
                    )
                    if golive_stage and project.stage_id == golive_stage and not project.survey_id:
                        survey = self.env['survey.survey'].create({
                            'title': 'Khảo sát GoLive - %s' % project.name,
                        })
                        project.survey_id = survey
        return res

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('dcg_project_customize.group_external_project_user'):
            raise AccessError(_('Bạn không có quyền tạo dự án mới.'))
        for vals in vals_list:
            lead = self.env['crm.lead']
            lead_id = vals.get('lead_id') or self.env.context.get('default_lead_id')
            if lead_id:
                lead = self.env['crm.lead'].browse(lead_id).exists()
            if lead:
                vals.setdefault('lead_id', lead.id)
                vals.setdefault('partner_id', lead.partner_id.id)
                vals.setdefault('user_id', lead.user_id.id)

        projects = super().create(vals_list)
        if projects:
            self.env['project.task.type']._dcg_standard_stages().write({
                'project_ids': [(4, project.id) for project in projects],
            })
        return projects

    @api.model
    def _dcg_assign_all_stages_to_all_projects(self):
        projects = self.with_context(active_test=False).search([])
        stages = self.env['project.task.type']._dcg_standard_stages()
        if projects and stages:
            stages.write({'project_ids': [(4, project.id) for project in projects]})

class ProjectHandoverChecklist(models.Model):
    _name = 'project.handover.checklist'
    _description = 'Checklist Tài Liệu Bàn Giao'

    project_id = fields.Many2one('project.project', string='Dự án', ondelete='cascade')
    name = fields.Char(string='Tên tài liệu', required=True)
    task_id = fields.Many2one('project.task', string='Task gốc')
    template_id = fields.Many2one(
        'project.stage.checklist.template',
        string='Mẫu checklist',
        readonly=True,
        ondelete='set null',
    )
    is_done = fields.Boolean(string='Đã bàn giao')
    handover_date = fields.Date(string='Ngày bàn giao', default=fields.Date.context_today)
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
