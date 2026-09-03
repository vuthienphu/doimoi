from odoo import models, fields


class SolutionModuleCommonIssue(models.Model):
    _name = 'solution.module.common.issue'
    _description = 'Lỗi thường gặp & Giải pháp'
    _order = 'severity desc, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Tên lỗi / Sự cố', required=True)
    description = fields.Text(string='Mô tả hiện tượng')
    cause = fields.Text(string='Nguyên nhân')
    solution = fields.Text(string='Giải pháp xử lý', required=True)
    severity = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('critical', 'Nghiêm trọng'),
    ], string='Mức độ', default='medium', required=True)
    version = fields.Selection([
        ('12', 'Odoo 12'),
        ('13', 'Odoo 13'),
        ('14', 'Odoo 14'),
        ('15', 'Odoo 15'),
        ('16', 'Odoo 16'),
        ('17', 'Odoo 17'),
        ('18', 'Odoo 18'),
        ('19', 'Odoo 19'),
    ], string='Phiên bản bị ảnh hưởng')
    image = fields.Binary(string='Hình ảnh minh họa')
    note = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Kích hoạt', default=True)
