# -*- coding: utf-8 -*-
import math
from datetime import date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

GROUP_CB = 'inom_employee_offboarding.inom_group_offboarding_officer'
GROUP_HRM = 'inom_employee_offboarding.inom_group_offboarding_hr'
GROUP_CEO = 'inom_employee_offboarding.inom_group_offboarding_ceo'

class InomOffboardingRequest(models.Model):
    _name = 'inom.offboarding.request'
    _description = 'Employee Offboarding Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Mã đơn', required=True, readonly=True,
                        index=True, default=lambda self: _('/'),)
    employee_id = fields.Many2one('hr.employee', 'Nhân viên', required=True, tracking=True,
                default=lambda self: self.env.user.employee_id.id)
    work_email = fields.Char('Email', required=True, readonly=True, tracking=True)
    contract_type_id = fields.Many2one('hr.contract.type', 'Loại hợp đồng', readonly=True, required=True, tracking=True)
    department_id = fields.Many2one('hr.department', 'Phòng ban', readonly=True, required=True, tracking=True)
    job_title = fields.Char('Chức danh', readonly=True, required=True, tracking=True)
    level_id = fields.Many2one('hr.level', 'Level', readonly=True, required=True, tracking=True)
    manager_id = fields.Many2one('hr.employee', 'Quản lý trực tiếp', readonly=True, required=True, tracking=True)
    
    offboarding_type = fields.Selection(
                    [('voluntarily', 'Nhân viên tự nguyện nghỉ'),
                    ('layoff', 'Công ty cho nghỉ')],
                    'Loại nghỉ việc', tracking=True)
    reason_id = fields.Many2one('inom.offboarding.reason', 'Lý do nghỉ việc', required=True, tracking=True)
    reason_id_require_extra = fields.Boolean(
        related='reason_id.require_extra_reason',
        string='Yêu cầu lý do cụ thể',
        readonly=True,
    )
    extra_reason = fields.Text(string='Lý do nghỉ việc khác', tracking=True)
    reason_manager_confirm_id = fields.Many2one('inom.offboarding.reason', 'Lý do nghỉ việc (QL ghi nhận)',
                                tracking=True)
    reason_manager_confirm_id_require_extra = fields.Boolean(
        related='reason_manager_confirm_id.require_extra_reason',
        string='Yêu cầu lý do cụ thể (QL ghi nhận)',
        readonly=True,
    )
    extra_reason_manager = fields.Text(string='Lý do nghỉ việc khác (QL ghi nhận)', tracking=True)
    proposed_last_day = fields.Date('Last Working Day dự kiến',
                                    required=True, tracking=True)
    last_day = fields.Date('Ngày nghỉ việc', tracking=True, readonly=True)

    employee_remarks = fields.Text(string='Ghi chú (từ Nhân viên)', tracking=True)
    hr_remarks = fields.Text(string='Ghi chú (từ HRM)')
    manager_remarks = fields.Text(string='Ghi chú (từ Quản lý)')

    rejection_reason = fields.Text(
        string='Lý do từ chối',
        readonly=True,
        copy=False,
        tracking=True
    )
    checklist_line_ids = fields.One2many(
        comodel_name='inom.offboarding.checklist.line',
        inverse_name='request_id',
        string='Clearance Checklist',
    )
    payment_line_ids = fields.One2many(
        comodel_name='inom.offboarding.payment.line',
        inverse_name='request_id',
        string='Khoản thanh toán',
    )
    checklist_progress = fields.Float(
        string='Tiến độ Checklist',
        compute='_compute_checklist_progress',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Nháp'),
            ('manager_approval', 'Quản lý duyệt'),
            ('hr_approval', 'HRM duyệt'),
            ('approved', 'Đã duyệt'),
            ('relieved', 'Đã nghỉ việc'),
            ('rejected', 'Từ chối'),
        ],
        string='Trạng thái',
        default='draft',
        tracking=True,
        copy=False,
    )
    active = fields.Boolean(string='Hoạt động', default=True, tracking=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Công ty',
        default=lambda self: self.env.company,
    )
    manager_approval_date = fields.Date(
        string='Ngày gửi duyệt quản lý',
        readonly=True,
        copy=False,
        help='Date when the request moved to the manager approval stage.',
    )
    hr_approval_date = fields.Date(
        string='Ngày gửi duyệt HR',
        readonly=True,
        copy=False,
        help='Date when the request moved to the HR approval stage.',
    )
    is_own_request = fields.Boolean(
        string='Is Own Request',
        compute='_compute_is_own_request',
    )
    is_manager = fields.Boolean(
        string='Is Manager of Employee',
        compute='_compute_is_manager',
    )
    is_created_request = fields.Boolean(
        string='Is Created Request',
        compute='_compute_is_created_request',
    )
    is_hrm = fields.Boolean(
        string='Is HRM',
        compute='_compute_uid',
    )
    is_cb = fields.Boolean(
        string='Is C&B',
        compute='_compute_uid',
    )
    is_ceo = fields.Boolean(
        string='Is CEO',
        compute='_compute_uid',
    )
    hide_reject = fields.Boolean(
        string='Ẩn nút từ chối',
        compute='_compute_hide_reject',
    )
    survey_user_input_id = fields.Many2one(
        'survey.user_input',
        string='Câu trả lời khảo sát',
        readonly=True,
        copy=False,
    )
    survey_user_input_state = fields.Selection(
        related='survey_user_input_id.state',
        string='Trạng thái khảo sát',
        readonly=True,
    )
    exit_interview_line_ids = fields.One2many(
        related='survey_user_input_id.user_input_line_ids',
        string='Form exit interview',
        readonly=True,
    )

    can_log_for_subordinates = fields.Boolean('Được tạo cho cấp dưới',
            compute='_compute_uid',
            help='Cờ kỹ thuật: True khi người dùng hiện tại là quản lý trực tiếp '
                 'của ít nhất một nhân viên, nên được tạo yêu cầu cho cấp dưới.')

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------
    @api.depends('employee_id')
    def _compute_is_own_request(self):
        for record in self:
            record.is_own_request = (
                            bool(record.employee_id.user_id)
                            and record.employee_id.user_id == self.env.user
                        )
            
    @api.depends('create_uid')
    def _compute_is_created_request(self):
        for record in self:
            record.is_created_request = (record.create_uid == self.env.user)

    @api.depends('manager_id')
    def _compute_is_manager(self):
        for record in self:
            record.is_manager = (record.manager_id.user_id == self.env.user)

    def _compute_uid(self):
        own_employees = self.env.user.sudo().employee_id
        has_subordinates = bool(own_employees) and bool(
            self.env['hr.employee'].sudo().search_count(
                [('parent_id', 'in', own_employees.ids),
                    ('active', '=', True)]))
        for record in self:
            record.can_log_for_subordinates = has_subordinates

            record.is_hrm = self.env.user.has_group(GROUP_HRM)
            record.is_cb = self.env.user.has_group(GROUP_CB)
            record.is_ceo = self.env.user.has_group(GROUP_CEO)

    @api.depends('state', 'manager_id')
    def _compute_hide_reject(self):
        for record in self:
            manager_user = record.manager_id.sudo().user_id
            record.hide_reject = (
                record.state not in ('manager_approval', 'hr_approval')
                or (record.state == 'manager_approval' and manager_user != self.env.user)
                or (record.state == 'hr_approval' and not self.env.user.has_group(GROUP_HRM))
            )

    @api.depends('checklist_line_ids', 'checklist_line_ids.is_done')
    def _compute_checklist_progress(self):
        for record in self:
            total = len(record.checklist_line_ids)
            done = len(record.checklist_line_ids.filtered('is_done'))
            record.checklist_progress = (done / total * 100.0) if total else 0

    # ------------------------------------------------------------------
    # Onchange
    # ------------------------------------------------------------------
    @api.onchange('employee_id')
    def _onchange_employee_details(self):
        # department_id của hr.employee là related qua version_id
        # (hr.version - dữ liệu hợp đồng), mà nhân viên thường không có quyền
        # đọc; dùng sudo để lấy các thông tin hiển thị này.
        employee = self.employee_id.sudo()
        self.department_id = employee.department_id
        self.work_email = employee.work_email
        self.job_title = employee.job_title
        self.manager_id = employee.parent_id
        self.level_id = employee.level_id
        self.contract_type_id = employee.contract_type_id

    @api.onchange('contract_type_id')
    def _onchange_contract_type(self):
        if self.contract_type_id:
            self.proposed_last_day = date.today() + timedelta(days=self.sudo().contract_type_id.min_notice_days)
            
    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains('proposed_last_day', 'create_date', 'employee_id')
    def _check_dates(self):
        for record in self:
            if record.employee_id != self.env.user.employee_id:
                continue

            notice_days = self.sudo().contract_type_id.min_notice_days
            date_check = date.today() + timedelta(days=notice_days)
            if record.proposed_last_day < date_check:
                raise ValidationError(_(
                    'Ngày làm việc cuối cùng dự kiến phải đảm bảo thời gian báo trước theo loại hợp đồng.'))

    @api.constrains('employee_id')
    def _check_creator(self):
        for rec in self:
            if self.env.user not in [rec.employee_id.user_id, rec.manager_id.user_id]:
                raise ValidationError(_(
                    'Bạn chỉ được tạo đơn cho bản thân hoặc nhân viên cấp dưới.'))
        
    @api.constrains('employee_id', 'state')
    def _check_employee_scope(self):
        for record in self:
            employee = record.employee_id.sudo()
            duplicated = record.sudo().search_count([
                        ('employee_id', '=', employee.id),
                        ('id', '!=', record.id),
                        ('state', 'not in', ['draft', 'rejected']),
                        ('active', '=', True)])
            if duplicated:
                raise ValidationError(_(
                    'Nhân viên này đã có đơn nghỉ việc đang xử lý hoặc đã '
                    'hoàn tất.'))
    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('/')) == _('/'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'inom.offboarding.request') or _('/')
        records = super().create(vals_list)
        for record in records:
            if record.manager_id.user_id and record.manager_id.user_id == record.create_uid:
                record.state = 'manager_approval'
                record.manager_approval_date = fields.Date.context_today(record)
        return records

    def unlink(self):
        cannot_del = self.filtered(lambda r: r.state != 'draft')
        if cannot_del:
            raise UserError(_('Chỉ cho phép xóa đơn xin nghỉ việc khi trạng thái hiện tại là Nháp.'))
        return super().unlink()

    def _can_archive(self):
        """Chỉ HRM hoặc C&B mới được lưu trữ / khôi phục bản ghi."""
        return (self.env.user.has_group(GROUP_HRM)
                or self.env.user.has_group(GROUP_CB))

    def write(self, vals):
        # Chặn thay đổi 'active' (lưu trữ/khôi phục) nếu không phải HRM/C&B.
        if 'active' in vals and not self.env.su and not self._can_archive():
            raise UserError(_(
                'Chỉ HRM hoặc C&B mới được lưu trữ / bỏ lưu trữ bản ghi.'))
        return super().write(vals)
    
    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_group_emails(self, group_xmlid):
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            return []
        return group.user_ids.mapped('login')

    @staticmethod
    def _join_emails(emails):
        """Nối danh sách email thành chuỗi, bỏ giá trị rỗng/False và trùng."""
        result = []
        for email in emails:
            if email and email not in result:
                result.append(email)
        return ','.join(result)

    def _get_record_url(self):
        """Return the backend form URL of this request (empty if unavailable)."""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        if self.id and base_url:
            return (
                '%s/web#id=%s&model=inom.offboarding.request&view_type=form'
                % (base_url, self.id))
        return ''

    def _get_approval_deadline(self, approval_date):
        """Format the approval deadline (approval_date + reminder delay)."""
        if not approval_date:
            return ''
        delay = self._get_reminder_delay_days()
        return (approval_date + timedelta(days=delay)).strftime('%d/%m/%Y')

    def _send_offboarding_mail(self, template_xmlid, recipient_email, context=None):
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return
        template.with_context(**(context or {})).send_mail(
            self.id,
            force_send=True,
            email_values={'email_to': recipient_email},
        )

    def action_start_exit_survey(self):
        """Open the exit interview survey for the requesting employee.

        Always uses the employee's linked user (``employee_id.user_id``) so
        the answer is recorded against the right person even if a manager or
        HR opens the form on their behalf.
        """
        self.ensure_one()
        survey = self.env.ref(
            'inom_employee_offboarding.offboarding_exit_interview_survey',
            raise_if_not_found=False)
        if not survey:
            raise UserError(_('Chưa cấu hình khảo sát nghỉ việc.'))
        employee_user = self.employee_id.user_id
        if not employee_user:
            raise UserError(_(
                'Nhân viên này chưa có tài khoản người dùng liên kết.'))
        if self.env.user != employee_user:
            raise UserError(_(
                'Bạn không có quyền làm khảo sát thay cho %s.',
            ) % self.employee_id.name)
        if not self.survey_user_input_id:
            answer = survey.sudo()._create_answer(user=employee_user)
            answer.manager_offboard_id = self.manager_id
            self.survey_user_input_id = answer
        else:
            answer = self.survey_user_input_id
        action = survey.sudo().action_start_survey(answer=answer)
        action['target'] = 'new'
        return action

    # ------------------------------------------------------------------
    # Workflow actions
    # ------------------------------------------------------------------
    def action_submit_to_manager(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_(
                    'Bản ghi này đã được cập nhật. Vui lòng làm mới trang.'))
            if record.create_uid == record.employee_id.user_id and record.survey_user_input_state != 'done':
                raise UserError(_(
                    'Bạn cần hoàn thành form khảo sát nghỉ việc trước khi '
                        'gửi đơn cho quản lý phê duyệt.'))
            record.state = 'manager_approval'
            record.manager_approval_date = fields.Date.context_today(record)
            emails = sum(
                (record._get_group_emails(g) for g in [GROUP_CB, GROUP_HRM, GROUP_CEO]),
                [record.manager_id.work_email],
            )
            context = {
                'record_url': record._get_record_url(),
                'manager_deadline': record._get_approval_deadline(
                    record.manager_approval_date),
            }
            record._send_offboarding_mail(
                'inom_employee_offboarding.mail_template_offboarding_submitted',
                record._join_emails(emails),
                context,
            )
        return True

    def action_manager_approve(self):
        for record in self:
            if record.state != 'manager_approval':
                raise UserError(_(
                    'Bản ghi này đã được cập nhật. Vui lòng làm mới trang.'))
            if record.manager_id.user_id != self.env.user:
                raise UserError(_(
                    'Bạn không phải là quản lý trực tiếp của nhân viên này.'))
            record.state = 'hr_approval'
            record.hr_approval_date = fields.Date.context_today(record)
            if not record.payment_line_ids:
                payment_templates = self.env['inom.offboarding.payment.template'].search([
                    '|',
                    ('company_id', '=', record.company_id.id),
                    ('company_id', '=', False),
                ])
                if payment_templates:
                    last_day_str = (
                        record.proposed_last_day.strftime('%d/%m/%Y')
                        if record.proposed_last_day else ''
                    )
                    record.sudo().payment_line_ids = [(0, 0, {
                        'template_id': tmpl.id,
                        'name': '%s %s' % (tmpl.name, last_day_str) if tmpl.append_last_day and last_day_str else tmpl.name,
                        'sequence': tmpl.sequence,
                        'notes': tmpl.notes,
                    }) for tmpl in payment_templates]
            hr_group = self.env.ref(GROUP_HRM)
            emails = [
                email
                for g in [GROUP_CB, GROUP_HRM, GROUP_CEO]
                for email in record._get_group_emails(g)
            ]
            context = {
                'record_url': record._get_record_url(),
                'hr_deadline': record._get_approval_deadline(record.hr_approval_date),
                'hr_recipient_name': ', '.join(hr_group.user_ids.employee_ids.mapped('name')) if hr_group else '',
            }
            record._send_offboarding_mail(
                'inom_employee_offboarding.mail_template_offboarding_hr_review',
                record._join_emails(emails),
                context)
        return True

    def action_hr_approve(self):
        for record in self:
            if record.state != 'hr_approval':
                raise UserError(_(
                    'Bản ghi này đã được cập nhật. Vui lòng làm mới trang.'))
            record.state = 'approved'
            if not self.checklist_line_ids:
                templates = self.env['inom.offboarding.checklist.template'].search([
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', '=', False),
                ])
                if templates:
                    self.sudo().checklist_line_ids = [(0, 0, {
                            'template_id': template.id,
                            'name': template.name,
                            'sequence': template.sequence,
                            'responsible': template.responsible,
                            'description': template.description,
                        }) for template in templates]
            emails = [
                record.employee_id.work_email,
                record.manager_id.work_email,
                *record._get_group_emails(GROUP_CEO),
            ]
            context = {'record_url': record._get_record_url()}
            record._send_offboarding_mail(
                'inom_employee_offboarding.mail_template_offboarding_approved',
                record._join_emails(emails),
                context)
        return True

    def action_relieve_employee(self):
        for record in self:
            if record.state != 'approved':
                raise UserError(_(
                    'Bản ghi này đã được cập nhật. Vui lòng làm mới trang.'))
            record.state = 'relieved'
            record.last_day = fields.Date.today()
            if record.employee_id:
                context = {'record_url': record._get_record_url()}
                record._send_offboarding_mail(
                    'inom_employee_offboarding.mail_template_offboarding_relieved',
                    record.employee_id.work_email,
                    context)
                record.employee_id.active = False
        return True

    def action_open_reject_wizard(self):
        self.ensure_one()
        is_hr = self.env.user.has_group(GROUP_HRM)
        is_manager = self.manager_id.user_id == self.env.user
        if not (is_hr or is_manager):
            raise UserError(_('Chỉ quản lý trực tiếp hoặc HRM mới có thể từ chối đơn này.'))
        return {
            'name': _('Từ chối đơn nghỉ việc'),
            'type': 'ir.actions.act_window',
            'res_model': 'inom.offboarding.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }

    def action_reset_to_draft(self):
        for record in self:
            if record.create_uid != self.env.user:
                raise UserError(_('Chỉ người tạo đơn mới có thể đưa về nháp.'))
            if record.state != 'rejected':
                raise UserError(_(
                    'Bản ghi này đã được cập nhật. Vui lòng làm mới trang.'))
            record.state = 'draft'
            record.rejection_reason = False
        return True

    def action_archive(self):
            if not self._can_archive():
                raise UserError(_(
                    'Bạn không có quyền lưu trữ.'))
            return super(InomOffboardingRequest, self.sudo()).action_archive()
    
    def action_unarchive(self):
        if not self._can_archive():
            raise UserError(_('Bạn không có quyền bỏ lưu trữ.'))
        return super(InomOffboardingRequest, self.sudo()).action_unarchive()

    # ------------------------------------------------------------------
    # Scheduled reminders
    # ------------------------------------------------------------------

    @api.model
    def _get_reminder_delay_days(self):
        '''Mặc định nhắc duyệt sau 5 ngày'''
        value = self.env['ir.config_parameter'].sudo().get_param(
                'inom_employee_offboarding.reminder_delay_days')
        if value:
            return int(value)
        else:
            return 5

    @api.model
    def _cron_send_approval_reminders(self):
        """Remind approvers when a request has been pending for too long.

        Only sends reminder emails; it never changes the workflow state or
        touches business data. Invoked by an ``ir.cron`` record.
        """
        today = fields.Date.context_today(self)
        deadline = today - timedelta(days=self._get_reminder_delay_days())

        # Step 1: requests stuck awaiting manager approval.
        manager_pending = self.search([
            ('state', '=', 'manager_approval'),
            ('manager_approval_date', '!=', False),
            ('manager_approval_date', '<=', deadline),
        ])
        for record in manager_pending:
            context = {
                'record_url': record._get_record_url(),
                'reminder_recipient_name': record.manager_id.name,
            }
            record._send_offboarding_mail(
                'inom_employee_offboarding.mail_template_offboarding_reminder',
                record.manager_id.work_email,
                context)

        # Step 2: requests stuck awaiting HR approval.
        hr_pending = self.search([
            ('state', '=', 'hr_approval'),
            ('hr_approval_date', '!=', False),
            ('hr_approval_date', '<=', deadline),
        ])
        hr_group = self.env.ref(GROUP_HRM)
        if hr_group:
            email_to = ', '.join(hr_group.user_ids.mapped('login'))
            name = ', '.join(hr_group.user_ids.employee_ids.mapped('name'))
            for record in hr_pending:
                context = {
                    'record_url': record._get_record_url(),
                    'reminder_recipient_name': name,
                }
                record._send_offboarding_mail(
                    'inom_employee_offboarding.mail_template_offboarding_reminder',
                     email_to,
                    context)

    @api.model
    def _cron_auto_relieve_due_requests(self):
        """Auto-relieve approved requests the day after their last working day.

        Runs daily; picks approved requests whose relieving date was yesterday
        (proposed_last_day + 1 == today) and relieve employee.
        """
        today = fields.Date.context_today(self)
        due_requests = self.search([
            ('state', '=', 'approved'),
            ('proposed_last_day', '<=', today - timedelta(days=1)),
        ])
        for record in due_requests:
            employee_lines = record.checklist_line_ids.filtered(
                lambda line: line.responsible == 'employee')
            if (employee_lines and all(employee_lines.mapped('is_done'))) \
            or not employee_lines:
                record.action_relieve_employee()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def _avg_tenure_years(self):
        """TB thâm niên (năm) của các đơn ĐÃ NGHỈ (relieved & chưa lưu trữ).

        Thâm niên 1 NV = (Ngày nghỉ việc - Ngày làm việc chính thức) / 365, làm
        tròn XUỐNG 1 chữ số. Trung bình rồi làm tròn xuống. False nếu không có.
        """
        tenures = []
        for record in self:
            if record.state != 'relieved' or not record.last_day:
                continue
            first_day = record.employee_id.sudo().official_start_date
            if not first_day:
                continue
            years = (record.last_day - first_day).days / 365.0
            if years >= 0:
                tenures.append(math.floor(years * 10) / 10.0)
        if not tenures:
            return False
        avg = sum(tenures) / len(tenures)
        return math.floor(avg * 10) / 10.0

    @api.model
    def get_dashboard_avg_tenure(self, domain):
        """Thâm niên TB khi nghỉ cho KPI (theo domain lọc của dashboard)."""
        return self.sudo().search(domain)._avg_tenure_years()

    def _headcount_at(self, date_point, dept_domain):
        """Số nhân viên đang làm việc TẠI thời điểm date_point.

        = đã vào làm (official_start_date <= date_point) VÀ chưa nghỉ tính đến
        thời điểm đó (không có đơn relieved với last_day < date_point). Gồm cả
        nhân viên inactive (đã lưu trữ).
        """
        employees = self.env['hr.employee'].sudo().search(
                    [('official_start_date', '!=', False),
                    ('official_start_date', '<=', date_point),
                    ('active', 'in', [True, False])] + dept_domain)
        if not employees:
            return 0
        # Đã nghỉ trước date_point -> loại khỏi headcount. Gắn theo đúng tập nhân
        # viên (đã bao hàm phòng ban) để không trừ nhầm sang phòng khác.
        left = self.sudo().search_count([
            ('state', '=', 'relieved'),
            ('employee_id', 'in', employees.ids),
            ('last_day', '<', date_point),
            ('active', '=', True)
        ])
        return len(employees) - left

    def _avg_headcount(self, start_date, end_date, dept_domain):
        """Trung bình headcount = (headcount đầu kỳ + headcount cuối kỳ) / 2."""
        return (
            self._headcount_at(start_date, dept_domain)
            + self._headcount_at(end_date, dept_domain)
        ) / 2.0

    def _turnover_ratio(self, leavers, headcount):
        """Tỷ lệ turnover (%) = leavers / headcount * 100, không âm.

        Trả về False nếu headcount <= 0.
        """
        if not headcount or headcount <= 0:
            return False
        return max(round(leavers / headcount * 100, 1), 0.0)

    def _turnover(self, leavers, start_date, end_date, dept_domain):
        """Tỷ lệ turnover (%) = leavers / ((headcount đầu kỳ + cuối kỳ) / 2) * 100.

        Mẫu số = trung bình headcount (đầu kỳ + cuối kỳ) / 2 — đúng bằng con số
        cột "Số lượng nhân sự". Dùng chung cho KPI và bảng phòng ban.
        """
        avg_headcount = self._avg_headcount(start_date, end_date, dept_domain)
        return self._turnover_ratio(leavers, avg_headcount)

    @api.model
    def get_dashboard_turnover(self, department_ids, start_date, end_date):
        """Turnover cho KPI. Kỳ = [start_date, end_date] (bao gồm 2 đầu).

        department_ids: danh sách phòng ban đang chọn (rỗng = tất cả).
        """
        dept_domain = [('department_id', 'in', department_ids)] if department_ids else []
        leavers = self.sudo().search_count(
            [('state', '=', 'relieved'),
             ('last_day', '>=', start_date),
             ('last_day', '<=', end_date),
             ('active', '=', True)
             ] + dept_domain)
        return self._turnover(leavers, start_date, end_date, dept_domain)

    @api.model
    def get_dashboard_department_rows(self, domain, start_date, end_date):
        """Trả về số liệu theo phòng ban cho dashboard.
        - headcount: trung bình (đầu kỳ + cuối kỳ) / 2.
        - leavers: số đơn nghỉ việc khớp domain.
        - top_reason: lý do được chọn nhiều nhất; nếu nhiều lý do bằng nhau ở
          mức cao nhất thì trả về tất cả.
        """
        rows = []
        for department, leavers in self._read_group(
                domain, ['department_id'], ['__count']):
            # Lý do nổi bật (xử lý đồng hạng).
            reason_groups = self._read_group(
                domain + [('department_id', '=', department.id)],
                ['reason_id'], ['__count'])
            top_reasons = []
            counted = [(reason, count) for reason, count in reason_groups if reason]
            if counted:
                max_count = max(count for _reason, count in counted)
                top_reasons = [reason.name for reason, count in counted if count == max_count]
            dept_domain = [('department_id', '=', department.id)]
            headcount = self._avg_headcount(
                start_date, end_date, dept_domain) if department else 0
            tenure = self.sudo().search(
                domain + dept_domain)._avg_tenure_years()
            # Turnover = leavers / "Số lượng nhân sự" (headcount trung bình).
            turnover = self._turnover_ratio(
                leavers, headcount) if department else False
            rows.append({
                'name': department.name if department else _('Không xác định'),
                'headcount': headcount,
                'leavers': leavers,
                'tenure': tenure,
                'turnover': turnover,
                'top_reasons': top_reasons,
            })
        rows.sort(key=lambda row: row['leavers'], reverse=True)
        return rows

    @api.model
    def get_dashboard_export_data(self, domain):
        """Trả về danh sách record cho xuất Excel dashboard.

        Mỗi phần tử là dict với các key: employee_code, employee_name,
        department, level, offboarding_type, reason, start_date, last_day,
        tenure_years, quarter, year.
        """
        OFFBOARDING_TYPE_LABELS = {
            'voluntarily': 'Nhân viên tự nguyện nghỉ',
            'layoff': 'Công ty cho nghỉ',
        }
        records = self.sudo().search(domain + [('state', '=', 'relieved')])
        rows = []
        for rec in records:
            employee = rec.employee_id.sudo()
            last_day = rec.last_day
            start_date = employee.official_start_date
            tenure = False
            if start_date and last_day:
                import math as _math
                tenure = _math.floor((last_day - start_date).days / 365 * 10) / 10
            quarter = False
            year = False
            if last_day:
                quarter = (last_day.month - 1) // 3 + 1
                year = last_day.year
            rows.append({
                'work_email': employee.work_email or '',
                'employee_name': employee.name or '',
                'department': rec.department_id.name if rec.department_id else '',
                'level': rec.level_id.name if rec.level_id else 'Không xác định',
                'offboarding_type': OFFBOARDING_TYPE_LABELS.get(rec.offboarding_type, rec.offboarding_type or ''),
                'reason': rec.reason_id.name if rec.reason_id else '',
                'start_date': start_date.strftime('%d/%m/%Y') if start_date else '',
                'last_day': last_day.strftime('%d/%m/%Y') if last_day else '',
                'tenure_years': tenure if tenure is not False else '',
                'quarter': quarter if quarter else '',
                'year': year if year else '',
            })
        return rows

    # ------------------------------------------------------------------
    # Báo cáo Excel (sheet "Báo cáo" + "Danh mục")
    # ------------------------------------------------------------------
    @api.model
    def _month_end(self, year, month):
        """Ngày đầu tháng kế tiếp (exclusive)."""
        return date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    @api.model
    def _week_buckets(self, year, month):
        """Chia tháng thành các tuần (Thứ 2 - CN), kẹp trong phạm vi tháng.
        Port từ _weekBuckets của dashboard JS."""
        days_in_month = (self._month_end(year, month) - date(year, month, 1)).days
        buckets = []
        day = 1
        while day <= days_in_month:
            dow = date(year, month, day).weekday()  # Mon=0..Sun=6
            end_day = min(day + (6 - dow), days_in_month)
            buckets.append((day, end_day))
            day = end_day + 1
        return buckets

    @api.model
    def _report_trend_buckets(self, year, quarter, month):
        """Danh sách bucket (label, start, end_exclusive) + tiêu đề, tùy filter.
        Bám đúng logic _trendBuckets của dashboard JS."""
        if month:
            buckets = []
            for start_day, end_day in self._week_buckets(year, month):
                buckets.append({
                    'label': 'Tuần %s-%s/%s' % (start_day, end_day, month),
                    'start': date(year, month, start_day),
                    'end': date(year, month, end_day) + timedelta(days=1),
                })
            return {'title': 'Số nghỉ việc theo tháng', 'buckets': buckets}
        if quarter:
            start_month = (quarter - 1) * 3 + 1
            buckets = []
            for i in range(3):
                m = start_month + i
                buckets.append({
                    'label': 'Tháng %s' % m,
                    'start': date(year, m, 1),
                    'end': self._month_end(year, m),
                })
            return {'title': 'Số nghỉ việc theo quý', 'buckets': buckets}
        # year
        buckets = []
        for q in (1, 2, 3, 4):
            sm = (q - 1) * 3 + 1
            em = sm + 3
            buckets.append({
                'label': 'Quý %s' % q,
                'start': date(year, sm, 1),
                'end': date(year + 1, em - 12, 1) if em > 12 else date(year, em, 1),
            })
        return {'title': 'Số nghỉ việc theo năm', 'buckets': buckets}

    @api.model
    def _report_period(self, year, quarter, month):
        """Ngày đầu/cuối kỳ (inclusive) cho tính turnover. Port từ _period JS."""
        if month:
            last_day = (self._month_end(year, month) - timedelta(days=1)).day
            return date(year, month, 1), date(year, month, last_day)
        if quarter:
            sm = (quarter - 1) * 3 + 1
            em = sm + 2
            last_day = (self._month_end(year, em) - timedelta(days=1)).day
            return date(year, sm, 1), date(year, em, last_day)
        return date(year, 1, 1), date(year, 12, 31)

    @api.model
    def get_report_export_data(self, domain, mode, year, quarter, month):
        """Số liệu cho sheet 'Báo cáo': KPI + trend + lý do + level.

        Tính sẵn trong Python theo đúng cơ chế bucket động của dashboard nên
        chart chỉ cần trỏ vào các ô giá trị (không dùng công thức COUNTIFS).
        """
        year = int(year) if year else 0
        quarter = int(quarter) if quarter else 0
        month = int(month) if month else 0

        # Tách domain phòng ban (bỏ các leaf lọc theo ngày) để đếm trend.
        dept_domain = [
            leaf for leaf in domain
            if not (isinstance(leaf, (list, tuple)) and leaf[0] == 'last_day')
        ]
        department_ids = []
        for leaf in domain:
            if isinstance(leaf, (list, tuple)) and leaf[0] == 'department_id':
                department_ids = leaf[2] if isinstance(leaf[2], (list, tuple)) else [leaf[2]]

        # KPI
        total = self.sudo().search_count(domain)
        start_date, end_date = self._report_period(year, quarter, month)
        turnover = self.get_dashboard_turnover(department_ids, start_date, end_date)
        tenure = self.get_dashboard_avg_tenure(domain)
        hc_dept_domain = [('department_id', 'in', department_ids)] if department_ids else []
        avg_headcount = self._avg_headcount(start_date, end_date, hc_dept_domain)

        # Trend (bucket động theo filter)
        trend = self._report_trend_buckets(year, quarter, month)
        trend_rows = []
        for b in trend['buckets']:
            base = dept_domain + [('last_day', '>=', b['start']), ('last_day', '<', b['end'])]
            vol = self.sudo().search_count(base + [('offboarding_type', '=', 'voluntarily')])
            lay = self.sudo().search_count(base + [('offboarding_type', '=', 'layoff')])
            trend_rows.append({'label': b['label'], 'vol': vol, 'lay': lay})

        # Lý do
        reasons = []
        for reason, count in self.sudo()._read_group(domain, ['reason_id'], ['__count']):
            reasons.append({'name': reason.name if reason else 'Không xác định', 'count': count})
        reasons.sort(key=lambda r: r['count'], reverse=True)

        # Level
        levels = []
        for level, count in self.sudo()._read_group(domain, ['level_id'], ['__count']):
            levels.append({'label': level.name if level else 'Không xác định', 'count': count})
        levels.sort(key=lambda r: r['count'], reverse=True)

        return {
            'kpi': {
                'total': total,
                'turnover': turnover if turnover is not False else 0.0,
                'tenure': tenure if tenure is not False else 0.0,
                'avg_headcount': avg_headcount,
            },
            'trend': {'title': trend['title'], 'rows': trend_rows},
            'reasons': reasons,
            'levels': levels,
        }

    @api.model
    def get_report_categories(self):
        """Danh mục cho sheet 'Danh mục', lấy động từ DB."""
        return {
            'departments': self.env['hr.department'].sudo().search([]).mapped('name'),
            'levels': self.env['hr.level'].sudo().search([]).mapped('name'),
            'offboarding_types': ['Nhân viên tự nguyện nghỉ', 'Công ty cho nghỉ'],
            'reasons': self.env['inom.offboarding.reason'].sudo().search([]).mapped('name'),
        }
