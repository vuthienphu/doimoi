# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # id_card / driving_license là field Binary core của hr.employee.
    # Chỉ thêm field lưu tên file để widget hiển thị tên + đuôi thay vì dung lượng.
    # groups="hr.group_hr_user": field custom nội bộ, phải gate để LOẠI khỏi
    # fallback public-profile của nhân viên thường (field không có trên
    # hr.employee.public → nếu accessible sẽ raise "không khả dụng cho hồ sơ công khai").
    id_card_filename = fields.Char('Tên file CCCD', groups="hr.group_hr_user")
    driving_license_filename = fields.Char('Tên file bằng lái', groups="hr.group_hr_user")

    official_start_date = fields.Date('Ngày làm việc chính thức',
                        compute='_compute_official_start_date',
                        store=True, compute_sudo=True, groups="hr.group_hr_user")

    # 3.1 Page Công việc
    work_type = fields.Selection([
        ('on_site', 'On-site'),
        ('office', 'Office'),
        ('remote', 'Remote'),
    ], string='Hình thức làm việc', required=True, default='office')

    seniority = fields.Float('Thâm niên', digits=(10, 2),
                             compute='_compute_seniority', store=True)
    archive_date = fields.Date('Ngày lưu trữ', groups="hr.group_hr_user")

    certificate = fields.Selection(
        selection=[
            ('thpt', 'THPT'),
            ('trung_cap', 'Trung cấp'),
            ('cao_dang', 'Cao đẳng'),
            ('bachelor', 'Đại học'),
            ('master', 'Thạc sĩ'),
            ('doctor', 'Tiến sĩ'),
        ],
        string='Certificate Level',
    )

    # 3.2 Page Cá nhân
    country_id = fields.Many2one(
        'res.country', default=lambda self: self.env.ref('base.vn', raise_if_not_found=False))

    vehicle_type = fields.Char('Loại phương tiện')

    id_issue_place = fields.Char('Nơi cấp')

    # Địa chỉ hiện tại
    current_street = fields.Char('Địa chỉ hiện tại')
    current_street2 = fields.Char('Địa chỉ hiện tại 2')
    current_city = fields.Char('Thành phố hiện tại')
    current_state_id = fields.Many2one('res.country.state', string='Tỉnh/Thành phố hiện tại')
    current_zip = fields.Char('ZIP hiện tại')
    current_country_id = fields.Many2one('res.country', string='Quốc gia hiện tại')

    # Liên hệ khẩn cấp - quan hệ
    emergency_relation = fields.Selection([
        ('bo', 'Bố'),
        ('me', 'Mẹ'),
        ('vo', 'Vợ'),
        ('chong', 'Chồng'),
        ('con', 'Con'),
        ('anh', 'Anh'),
        ('chi', 'Chị'),
        ('em', 'Em'),
        ('ong', 'Ông'),
        ('ba', 'Bà'),
        ('other', 'Người thân khác'),
    ], string='Mối quan hệ (khẩn cấp)')

    # Gia đình
    family_member_ids = fields.One2many('hr.employee.relative', 'employee_id',
                                        string='Thành viên gia đình',
                                        domain=[('type', '=', 'family')])

    # Người phụ thuộc
    dependent_ids = fields.One2many('hr.employee.relative', 'employee_id',
                                    string='Người phụ thuộc',
                                    domain=[('type', '=', 'dependent')])

    # Thông tin Thuế & BHXH
    bank_id = fields.Many2one('res.bank', string='Ngân hàng')
    initial_hospital_id = fields.Many2one('hr.hospital', string='Nơi đăng ký bệnh viện ban đầu')
    tax_code = fields.Char('Mã số thuế')
    bank_account_number = fields.Char('Tài khoản ngân hàng')

    # 3.3 Page Hợp đồng
    legal_entity_id = fields.Many2one('hr.contract.legal.entity',
                                       string='Pháp nhân ký hợp đồng',
                                       required=True)
    contract_status = fields.Selection([
        ('active', 'Hiệu lực'),
        ('expired', 'Hết hiệu lực'),
    ], string='Trạng thái hợp đồng', required=True)

    # 3.4 Quá trình công tác
    work_history_ids = fields.One2many('hr.employee.work.history', 'employee_id',
                                       string='Quá trình công tác')

    # ── Bỏ hạn chế groups (hr.group_hr_user) trên các field core (định nghĩa
    #    trực tiếp trên hr.employee) để CEO và nhân viên (public) đều xem được.
    #    Field delegated từ hr.version được xử lý riêng trong hr_version.py. ──
    private_email = fields.Char(groups=False)
    birthday = fields.Date(groups=False)
    emergency_contact = fields.Char(groups=False)
    emergency_phone = fields.Char(groups=False)
    certificate = fields.Selection(groups=False)
    study_field = fields.Char(groups=False)
    study_school = fields.Char(groups=False)
    private_car_plate = fields.Char(groups=False)

    # Computed fields để dùng trong readonly domain trên view
    is_cb = fields.Boolean(compute='_compute_is_cb', string='Is C&B')
    is_hrm = fields.Boolean(compute='_compute_is_hrm', string='Is HRM')

    def _compute_is_cb(self):
        is_cb = self.env.user.has_group('hr.group_hr_manager')
        for rec in self:
            rec.is_cb = is_cb

    def _compute_is_hrm(self):
        is_hrm = self.env.user.has_group('hr.group_hr_user')
        for rec in self:
            rec.is_hrm = is_hrm

    def _has_field_access(self, field, operation):
        # CEO có ACL read (read-only) trên hr.employee và cần xem TẤT CẢ field
        # trên form private. Cấp quyền ĐỌC mọi field cho CEO (trừ field NO_ACCESS
        # '.'). KHÔNG dùng groups=False trên từng field vì như vậy sẽ mở field cho
        # nhân viên thường → vỡ cơ chế public-profile fallback của hr.employee
        # (fetch field không có trên hr.employee.public → AccessError).
        if (operation == 'read' and not self.env.su
                and field.groups != '.'
                and self.env.user.has_group('hr_custom.group_hr_ceo')):
            return True
        return super()._has_field_access(field, operation)

    @api.depends('version_ids.contract_date_start')
    def _compute_official_start_date(self):
        for employee in self:
            starts = employee.version_ids.filtered(
                'contract_date_start').mapped('contract_date_start')
            employee.official_start_date = min(starts) if starts else False

    @api.depends('official_start_date', 'archive_date', 'active')
    def _compute_seniority(self):
        today = fields.Date.today()
        for employee in self:
            if not employee.official_start_date:
                employee.seniority = 0.0
                continue
            if not employee.active and employee.archive_date:
                end = employee.archive_date
            else:
                end = today
            delta = end - employee.official_start_date
            employee.seniority = round(delta.days / 365.25, 2)

    @api.onchange('work_phone', 'mobile_phone', 'company_country_id', 'company_id')
    def _onchange_phone_validation_employee(self):
        # Ghi đè core để không tự format số thành +84
        pass

    @api.constrains('birthday')
    def _check_birthday(self):
        today = fields.Date.today()
        for rec in self:
            if rec.birthday and rec.birthday > today:
                raise ValidationError('Ngày sinh không được là ngày trong tương lai.')

    _FIELD_VALIDATIONS = {
        'identification_id': (r'[0-9]{1,20}','Số định danh cá nhân chỉ được chứa chữ số và có độ dài từ 1 đến 20 ký tự.'),
        'ssnid':             (r'[0-9]{1,10}','Mã số BHXH chỉ được chứa chữ số và có độ dài từ 1 đến 10 ký tự.'),
    }

    def _validate_custom_fields(self, vals):
        for field, (pattern, error) in self._FIELD_VALIDATIONS.items():
            if field in vals and vals[field] and not re.fullmatch(pattern, vals[field]):
                raise ValidationError(error)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._validate_custom_fields(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._validate_custom_fields(vals)
        if 'active' in vals and not vals['active'] and 'archive_date' not in vals:
            vals['archive_date'] = fields.Date.today()
        return super().write(vals)

    @api.constrains('private_email')
    def _check_private_email(self):
        email_re = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        for rec in self:
            if rec.private_email and not email_re.match(rec.private_email):
                raise ValidationError('Email cá nhân không đúng định dạng. Định dạng hợp lệ: example@domain.com')

    @api.constrains('work_email')
    def _check_work_email(self):
        email_re = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        for rec in self:
            if rec.work_email and not email_re.match(rec.work_email):
                raise ValidationError('Email công việc không đúng định dạng. Định dạng hợp lệ: example@domain.com')

    @api.constrains('mobile_phone')
    def _check_mobile_phone(self):
        for rec in self:
            if rec.mobile_phone and not re.match(r'^\d{10}$', rec.mobile_phone):
                raise ValidationError('Số điện thoại phải gồm đúng 10 chữ số.')

    @api.constrains('emergency_phone')
    def _check_emergency_phone(self):
        for rec in self:
            if rec.emergency_phone and not re.match(r'^\d{10}$', rec.emergency_phone):
                raise ValidationError('Số điện thoại liên hệ khẩn cấp phải gồm đúng 10 chữ số.')

    @api.constrains('bank_account_number')
    def _check_bank_account_number(self):
        for rec in self:
            if rec.bank_account_number and len(rec.bank_account_number) > 20:
                raise ValidationError('Tài khoản ngân hàng tối đa 20 ký tự.')

    @api.constrains('tax_code')
    def _check_tax_code(self):
        for rec in self:
            if rec.tax_code and not re.match(r'^\d{10}$|^\d{13}$', rec.tax_code):
                raise ValidationError('Mã số thuế phải là 10 hoặc 13 chữ số.')
