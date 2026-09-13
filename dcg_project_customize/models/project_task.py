# -*- coding: utf-8 -*-

from email.utils import formataddr
from markupsafe import Markup

import odoo
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    _MANAGER_EDITABLE_FIELDS = {
        'date_deadline',
        'request_date',
        'reviewer_ids',
        'user_ids',
        'project_id',
        'estimate_hours',
        'tag_ids',
        'description',
        'checklist_ids',
    }

    can_edit_manager_fields = fields.Boolean(
        string='Có thể chỉnh sửa các trường quản lý',
        compute='_compute_can_edit_manager_fields',
    )
    is_external_project_user = fields.Boolean(
        compute='_compute_is_external_project_user',
    )

    reviewer_ids = fields.Many2many(
        'res.users',
        'project_task_reviewer_rel',
        'task_id',
        'user_id',
        string='Danh sách người kiểm tra',
    )
    request_date = fields.Date(
        string='Ngày yêu cầu',
        default=fields.Date.context_today,
        copy=False,
    )
    requester_id = fields.Many2one('res.partner', string='Người yêu cầu')
    customer_company_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        related='project_id.partner_id',
        readonly=True,
    )
    planned_finish_date = fields.Datetime(string='Thời gian dự kiến hoàn thành')
    actual_finish_date = fields.Datetime(string='Thời gian thực tế hoàn thành', readonly=True)
    checklist_ids = fields.One2many(
        'task.checklist',
        'task_id',
        string='Danh sách checklist',
    )
    is_draft = fields.Boolean(related='stage_id.is_draft', string='Bản nháp', readonly=True)
    estimate_hours = fields.Float(string='Số giờ estimate')
    actual_hours = fields.Float(
        string='Số giờ hoàn thành thực tế',
        compute='_compute_actual_hours',
        store=True,
    )
    work_log_ids = fields.One2many(
        'project.task.work.log',
        'task_id',
        string='Lịch sử làm việc',
    )
    current_user_status = fields.Selection([
        ('not_started', 'Chưa bắt đầu'),
        ('running', 'Đang thực hiện'),
        ('paused', 'Tạm dừng'),
        ('finished', 'Đã kết thúc'),
    ], string='Trạng thái thực hiện (Cá nhân)', compute='_compute_current_user_status')
    is_over_estimate = fields.Boolean(compute='_compute_is_over_estimate')
    is_over_deadline = fields.Boolean(compute='_compute_is_over_deadline')
    over_deadline_reason = fields.Text(string='Lý do quá hạn', readonly=True)
    
    is_current_user_assignee = fields.Boolean(compute='_compute_is_current_user_assignee')
    project_member_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_project_member_user_ids',
        string='Người dùng trong dự án'
    )
    task_type= fields.Selection([
        ('feature','Chức năng'),
        ('bug','Lỗi'),
        ('enhancement','Cải tiến'),
        ('change','Thay đổi'),
        ('technical','Kỹ thuật'),
        ('documentation','Tài liệu')
    ],string='Phân loại Task')
    is_live=fields.Boolean(related='stage_id.is_live',string='Đã Go-live',readonly=True)
    bug_reason=fields.Text(string='Nguyên nhân')
    bug_solution=fields.Text(string='Cách xử lý')

    @api.depends_context('uid')
    def _compute_can_edit_manager_fields(self):
        can_edit = self.env.user.has_group('project.group_project_manager')
        for task in self:
            task.can_edit_manager_fields = can_edit

    @api.depends_context('uid')
    def _compute_is_external_project_user(self):
        is_external = self.env.user.has_group(
            'dcg_project_customize.group_external_project_user'
        )
        for task in self:
            task.is_external_project_user = is_external

    @api.depends('project_id.member_ids.user_id')
    def _compute_project_member_user_ids(self):
        for task in self:
            task.project_member_user_ids = task.project_id.sudo().member_ids.mapped('user_id')

    @api.depends('user_ids')
    def _compute_is_current_user_assignee(self):
        for task in self:
            task.is_current_user_assignee = self.env.user in task.user_ids

    @api.depends('work_log_ids.duration')
    def _compute_actual_hours(self):
        for task in self:
            task.actual_hours = sum(task.work_log_ids.mapped('duration'))

    @api.depends('work_log_ids.is_running', 'work_log_ids.user_id', 'stage_id.is_done', 'stage_id.is_live')
    def _compute_current_user_status(self):
        for task in self:
            if task.stage_id.is_done or task.stage_id.is_live:
                task.current_user_status = 'finished'
                continue

            user_logs = task.work_log_ids.filtered(lambda l: l.user_id == self.env.user)
            if user_logs.filtered('is_running'):
                task.current_user_status = 'running'
            elif user_logs:
                task.current_user_status = 'paused'
            else:
                task.current_user_status = 'not_started'

    @api.depends('actual_hours', 'estimate_hours')
    def _compute_is_over_estimate(self):
        for task in self:
            task.is_over_estimate = task.estimate_hours > 0 and task.actual_hours > task.estimate_hours

    @api.depends('date_deadline', 'stage_id.is_done', 'stage_id.is_live')
    def _compute_is_over_deadline(self):
        for task in self:
            if task.date_deadline and not (task.stage_id.is_done or task.stage_id.is_live):
                if hasattr(task.date_deadline, 'hour'):
                    task.is_over_deadline = fields.Datetime.now() > task.date_deadline
                else:
                    task.is_over_deadline = fields.Date.today() > task.date_deadline
            else:
                task.is_over_deadline = False

    def action_timer_start(self):
        self.ensure_one()
        running_log = self.work_log_ids.filtered(lambda l: l.user_id == self.env.user and l.is_running)
        if running_log:
            raise odoo.exceptions.UserError('Bạn đang có một phiên làm việc đang chạy trên task này.')
            

        self.env['project.task.work.log'].create({
            'task_id': self.id,
            'user_id': self.env.user.id,
            'start_time': fields.Datetime.now(),
        })
        
        if self.stage_id.is_draft:
            processing_stage = self.env['project.task.type'].search([('is_processing', '=', True)], limit=1)
            if processing_stage:
                self.stage_id = processing_stage.id

    def action_timer_pause(self):
        self.ensure_one()
        running_log = self.work_log_ids.filtered(lambda l: l.user_id == self.env.user and l.is_running)
        if running_log:
            running_log.write({'end_time': fields.Datetime.now()})

    def action_timer_stop(self):
        self.ensure_one()
        if self.is_over_deadline and not self.over_deadline_reason:
            return {
                'name': 'Nhập lý do quá hạn',
                'type': 'ir.actions.act_window',
                'res_model': 'project.task.finish.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_task_id': self.id},
            }
        self.action_timer_pause()
        done_stage = self.env['project.task.type'].search([('is_done', '=', True)], limit=1)
        if done_stage:
            self.stage_id = done_stage.id

    def action_open_subtasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công việc con',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
                'default_project_id': self.project_id.id,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('dcg_project_customize.group_external_project_user'):
            allowed_project_ids = set(self.env['project.project'].search([
                ('external_user_ids', 'in', self.env.user.id),
            ]).ids)
            for vals in vals_list:
                project_id = vals.get('project_id') or self.env.context.get('default_project_id')
                if not project_id or project_id not in allowed_project_ids:
                    raise AccessError(_('Bạn chỉ có thể tạo task trong dự án đã được cấp quyền.'))
                vals['user_ids'] = [(5, 0, 0)]
                vals['reviewer_ids'] = [(5, 0, 0)]
        tasks = super(ProjectTask, self.with_context(dcg_task_creation=True)).create(vals_list)
        tasks = tasks.with_env(self.env)
        for task in tasks:
            task._auto_subscribe_related_users()
        return tasks

    def write(self, vals):
        protected_fields = self._MANAGER_EDITABLE_FIELDS.intersection(vals)
        if (
            protected_fields
            and not self.env.su
            and not self.env.user.has_group('project.group_project_manager')
        ):
            field_labels = sorted(
                self._fields[field_name].string for field_name in protected_fields
            )
            raise UserError(_(
                'Bạn cần có quyền Quản lý dự án để chỉnh sửa các trường: %s'
            ) % ', '.join(field_labels))

        if 'stage_id' in vals:
            stage = self.env['project.task.type'].browse(vals['stage_id'])
            if stage.is_done:
                unfinished_tasks = self.filtered(lambda task: not task.actual_finish_date)
                if unfinished_tasks:
                    super(ProjectTask, unfinished_tasks).write({
                        'actual_finish_date': fields.Datetime.now(),
                    })
        result = super().write(vals)
        if 'reviewer_ids' in vals or 'user_ids' in vals:
            for task in self:
                task._auto_subscribe_related_users()
        if 'stage_id' in vals and not self.env.context.get('dcg_skip_stage_notification'):
            for task in self:
                task._send_stage_notification()
        return result

    def _auto_subscribe_related_users(self):
        for task in self:
            users_to_subscribe = task.reviewer_ids
            for user in task.user_ids:
                employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
                if employee and employee.parent_id and employee.parent_id.user_id:
                    users_to_subscribe |= employee.parent_id.user_id
            if users_to_subscribe:
                partner_ids = users_to_subscribe.mapped('partner_id').ids
                existing_partners = task.message_follower_ids.mapped('partner_id').ids
                new_partners = [p for p in partner_ids if p not in existing_partners]
                
                task.message_subscribe(partner_ids=partner_ids)
                
                if new_partners:
                    # Lọc bỏ địa chỉ trùng với alias của CRM để không bắn mail vào hòm thư CRM
                    crm_aliases = set(self.env['mail.alias'].sudo().search([
                        ('alias_model_id.model', '=', 'crm.lead'),
                        ('alias_name', '!=', False),
                    ]).mapped('alias_name'))

                    valid_partners = []
                    for partner in self.env['res.partner'].browse(new_partners):
                        if partner.email:
                            local_part = partner.email.split('@')[0].strip().lower()
                            if local_part in crm_aliases:
                                continue
                        valid_partners.append(partner.id)

                    if valid_partners:
                        deadline_str = task.date_deadline.strftime('%d/%m/%Y') if task.date_deadline else 'Chưa đặt'
                        task_url = task._get_task_url()
                        body_html = Markup(
                            '<p>Xin chào,</p>'
                            '<p>Bạn vừa được thêm vào theo dõi công việc <b>%s</b> (vai trò Người kiểm tra / Quản lý).</p>'
                            '<ul>'
                            '<li><b>Dự án:</b> %s</li>'
                            '<li><b>Khách hàng:</b> %s</li>'
                            '<li><b>Hạn chót:</b> %s</li>'
                            '</ul>'
                            '<p style="margin-top: 15px;">'
                            '<a href="%s" style="padding: 10px 20px; background-color: #875A7B; color: #ffffff; text-decoration: none; border-radius: 4px; display: inline-block;">'
                            'Mở công việc'
                            '</a>'
                            '</p>'
                        ) % (
                            task.name,
                            task.project_id.name or '',
                            task.partner_id.name or '',
                            deadline_str,
                            task_url,
                        )
                        task.message_post(
                            body=body_html,
                            partner_ids=valid_partners,
                            subject="[Task] %s - Thông báo người theo dõi" % task.name,
                            subtype_xmlid='mail.mt_comment',
                            message_type='comment',
                        )

    def _send_stage_notification(self):
        self.ensure_one()
        stage = self.stage_id
        if stage.is_processing:
            self._send_mail_processing()
        elif stage.is_test:
            self._send_mail_test()
        elif stage.is_done:
            self._send_mail_done()

    def _send_mail_processing(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_processing_notify',
            self.create_uid,
        )

    def _send_mail_test(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_test_notify',
            self.reviewer_ids,
        )

    def _send_mail_done(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_done_notify',
            self.create_uid | self.user_ids,
        )

    def _send_reminder_processing(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_reminder_processing',
            self.create_uid | self.user_ids,
        )

    def _send_reminder_test(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_reminder_test',
            self.create_uid | self.user_ids | self.reviewer_ids,
        )

    def _send_reminder_done_not_live(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_reminder_done_not_live',
            self.create_uid | self.user_ids,
        )

    def _send_task_template(self, template_xmlid, users):
        self.ensure_one()
        
        all_users = users | self.reviewer_ids
        for user in self.user_ids:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            if employee and employee.parent_id and employee.parent_id.user_id:
                all_users |= employee.parent_id.user_id
                
        emails = list(dict.fromkeys(all_users.filtered(lambda user: user.email).mapped('email')))
        if not emails:
            return False

        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return False

        return template.send_mail(
            self.id,
            force_send=True,
            email_values={'email_to': ','.join(emails)},
        )

    def _get_task_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return '%s/web#id=%s&model=project.task&view_type=form' % (base_url, self.id)

    def _get_mail_from(self):
        self.ensure_one()
        config = self.env['ir.config_parameter'].sudo()
        company = self.env.company
        email = (
            config.get_param('dcg_project_customize.mail_from')
            or company.email
            or self.env.user.email
        )
        if not email:
            return ''

        name = (
            config.get_param('dcg_project_customize.mail_from_name')
            or company.name
            or self.env.user.name
        )
        return formataddr((name, email)) if name else email
    def action_send_reminder(self):
        for task in self:
            if not task.user_ids:
                continue
            task._send_task_template('dcg_project_customize.task_processing_notify',task.user_ids)
            task.message_post(body="Đã gửi email nhắc nhở thực hiện công việc")
    def action_open_document_wizard(self):
        self.ensure_one()
        return{
            'name':'Lưu trữ tài liệu',
            'type':'ir.actions.act_window',
            'res_model':'project.task.document.wizard',
            'view_mode':'form',
            'target':'new',
            'context':{
                'default_task_id':self.id,
                'default_project_id':self.project_id.id,
            }
        }
    @api.model
    def _cron_send_daily_reminders(self):
        processing = self.search([('stage_id.is_processing', '=', True)])
        for task in processing:
            task._send_reminder_processing()

        testing = self.search([('stage_id.is_test', '=', True)])
        for task in testing:
            task._send_reminder_test()

        done_not_live = self.search([
            ('stage_id.is_done', '=', True),
            ('stage_id.is_live', '=', False),
        ])
        for task in done_not_live:
            task._send_reminder_done_not_live()

class TaskDocumentWizard(models.TransientModel):
    _name = 'project.task.document.wizard'
    _description = 'Popup lưu trữ tài liệu'

    task_id = fields.Many2one('project.task', required=True)
    project_id = fields.Many2one('project.project', required=True)
    name = fields.Char(string='Tên tài liệu', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    is_handed_over = fields.Boolean(string='Đã bàn giao khách hàng')
    handover_date = fields.Date(string='Ngày bàn giao')

    def action_confirm(self):
        existing_doc = self.env['project.handover.checklist'].search([
            ('task_id', '=', self.task_id.id)
        ], limit=1)
        val = {
            'name': self.name,
            'project_id': self.project_id.id,
            'task_id': self.task_id.id,
            'is_done': self.is_handed_over,
            'handover_date': self.handover_date,
            'attachment_ids': [(6, 0, self.attachment_ids.ids)]
        }
        if existing_doc:
            existing_doc.write(val)
        else:
            self.env['project.handover.checklist'].create(val)
