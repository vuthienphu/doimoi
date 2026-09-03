# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re

RELATION_SELECTION = [
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
    ('khac', 'Người thân khác'),
]

FIELD_VALIDATIONS = {
    'identification_id': (r'[0-9]{1,20}','Số CCCD chỉ được chứa chữ số (tối đa 20 ký tự).'),
    'tax_code': (r'[0-9]{10}|[0-9]{13}','Mã số thuế phải là 10 hoặc 13 chữ số.'),
}


class HrEmployeeRelative(models.Model):
    _name = 'hr.employee.relative'
    _description = 'Thành viên gia đình / Người phụ thuộc'
    _order = 'sequence, id'

    employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade')
    type = fields.Selection([
        ('family', 'Thành viên gia đình'),
        ('dependent', 'Người phụ thuộc'),
    ], required=True)
    sequence = fields.Integer(default=10)
    relation = fields.Selection(RELATION_SELECTION, string='Quan hệ', required=True)
    name = fields.Char('Họ và tên', required=True)

    # Chỉ dùng cho người phụ thuộc
    birthday = fields.Date('Ngày sinh')
    identification_id = fields.Char('Số CCCD')
    tax_code = fields.Char('Mã số thuế')
    deduction_start = fields.Date('Ngày bắt đầu tính giảm trừ')
    deduction_end = fields.Date('Ngày kết thúc tính giảm trừ')

    def _validate_custom_fields(self, vals):
        for field, (pattern, error) in FIELD_VALIDATIONS.items():
            if field in vals and vals[field] and not re.fullmatch(pattern, vals[field]):
                raise ValidationError(error)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._validate_custom_fields(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._validate_custom_fields(vals)
        return super().write(vals)

    @api.constrains('type', 'birthday', 'identification_id', 'tax_code')
    def _check_dependent_required(self):
        for rec in self:
            if rec.type == 'dependent':
                missing = []
                if not rec.birthday:
                    missing.append('Ngày sinh')
                if not rec.identification_id:
                    missing.append('Số CCCD')
                if not rec.tax_code:
                    missing.append('Mã số thuế')
                if missing:
                    raise ValidationError(
                        _('Người phụ thuộc bắt buộc nhập: %s') % ', '.join(missing)
                    )

    @api.constrains('birthday')
    def _check_birthday(self):
        today = fields.Date.today()
        for rec in self:
            if rec.birthday and rec.birthday > today:
                raise ValidationError(_('Ngày sinh không được là ngày trong tương lai.'))

    @api.constrains('deduction_start', 'deduction_end')
    def _check_deduction_dates(self):
        for rec in self:
            if rec.deduction_start and rec.deduction_end and rec.deduction_start > rec.deduction_end:
                raise ValidationError(
                    _('Ngày bắt đầu tính giảm trừ phải trước hoặc bằng ngày kết thúc.')
                )
