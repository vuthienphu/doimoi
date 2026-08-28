# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    # True nếu user hiện tại được phép MỞ form của bản ghi này:
    #  - thuộc bất kỳ nhóm HR nào (C&B/HRM/CEO), hoặc
    #  - là chính mình.
    # Non-HR user KHÔNG xem được form của bất kỳ ai khác (kể cả cấp dưới).
    # Dùng để chặn mở form ở client (list/kanban) và cả khi vào bằng URL.
    can_open_form = fields.Boolean(
        string='Được mở form',
        compute='_compute_can_open_form',
        compute_sudo=True,
    )

    def _compute_can_open_form(self):
        user = self.env.user
        is_hr = (user.has_group('hr.group_hr_user')
                 or user.has_group('hr_custom.group_hr_ceo'))
        for rec in self:
            rec.can_open_form = is_hr or (rec.user_id.id == user.id)

    # Toàn bộ field lấy related từ hr.employee (readonly).
    # LƯU Ý BẢO MẬT: các field lương/thuế/BHXH/ngân hàng sẽ hiển thị cho MỌI
    # nhân viên trên màn public — theo yêu cầu của người dùng.

    # Công việc
    # groups=False: ghi đè group kế thừa từ field nguồn (hr.employee/hr.version)
    # để CEO (không thuộc hr.group_hr_user/manager) vẫn xem được trên public.
    work_type = fields.Selection(related='employee_id.work_type')
    seniority = fields.Float(related='employee_id.seniority')
    contract_type_id = fields.Many2one(related='employee_id.contract_type_id', groups=False, compute_sudo=True)
    legal_entity_id = fields.Many2one(related='employee_id.legal_entity_id')
    contract_status = fields.Selection(related='employee_id.contract_status')
    contract_date_start = fields.Date(related='employee_id.contract_date_start', groups=False, compute_sudo=True)
    contract_date_end = fields.Date(related='employee_id.contract_date_end', groups=False, compute_sudo=True)

    # Cá nhân
    private_email = fields.Char(related='employee_id.private_email')
    birthday = fields.Date(related='employee_id.birthday')
    sex = fields.Selection(related='employee_id.sex')
    vehicle_type = fields.Char(related='employee_id.vehicle_type')
    private_car_plate = fields.Char(related='employee_id.private_car_plate')
    marital = fields.Selection(related='employee_id.marital')
    emergency_contact = fields.Char(related='employee_id.emergency_contact')
    emergency_relation = fields.Selection(related='employee_id.emergency_relation')
    emergency_phone = fields.Char(related='employee_id.emergency_phone')

    # Công dân
    country_id = fields.Many2one(related='employee_id.country_id')
    identification_id = fields.Char(related='employee_id.identification_id')
    id_issue_place = fields.Char(related='employee_id.id_issue_place')

    # Địa chỉ thường trú
    private_street = fields.Char(related='employee_id.private_street')
    private_street2 = fields.Char(related='employee_id.private_street2')
    private_city = fields.Char(related='employee_id.private_city')
    private_state_id = fields.Many2one(related='employee_id.private_state_id')
    private_zip = fields.Char(related='employee_id.private_zip')
    private_country_id = fields.Many2one(related='employee_id.private_country_id')

    # Địa chỉ hiện tại
    current_street = fields.Char(related='employee_id.current_street')
    current_street2 = fields.Char(related='employee_id.current_street2')
    current_city = fields.Char(related='employee_id.current_city')
    current_state_id = fields.Many2one(related='employee_id.current_state_id')
    current_zip = fields.Char(related='employee_id.current_zip')
    current_country_id = fields.Many2one(related='employee_id.current_country_id')

    # Học vấn
    certificate = fields.Selection(related='employee_id.certificate')
    study_field = fields.Char(related='employee_id.study_field')
    study_school = fields.Char(related='employee_id.study_school')

    # Thuế & BHXH
    bank_id = fields.Many2one(related='employee_id.bank_id')
    bank_account_number = fields.Char(related='employee_id.bank_account_number')
    ssnid = fields.Char(related='employee_id.ssnid')
    initial_hospital_id = fields.Many2one(related='employee_id.initial_hospital_id')
    tax_code = fields.Char(related='employee_id.tax_code')

    # Công việc (bổ sung) — groups=False + compute_sudo để CEO xem được
    level_id = fields.Many2one(related='employee_id.level_id', groups=False, compute_sudo=True)
    category_ids = fields.Many2many(related='employee_id.category_ids', groups=False, compute_sudo=True)

    # One2many
    family_member_ids = fields.One2many(related='employee_id.family_member_ids')
    dependent_ids = fields.One2many(related='employee_id.dependent_ids')
    work_history_ids = fields.One2many(related='employee_id.work_history_ids')
