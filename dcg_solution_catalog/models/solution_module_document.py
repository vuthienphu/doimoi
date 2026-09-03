from odoo import models, fields


class SolutionModuleDocument(models.Model):
    _name = 'solution.module.document'
    _description = 'Tài liệu Giải pháp'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Tên tài liệu', required=True)
    document_type = fields.Selection([
        ('user_manual', 'Hướng dẫn sử dụng'),
        ('business_doc', 'Tài liệu nghiệp vụ'),
        ('technical_doc', 'Tài liệu kỹ thuật'),
        ('config_doc', 'Tài liệu cấu hình'),
        ('test_case', 'Test Case'),
        ('uat', 'UAT'),
        ('training', 'Training'),
        ('deployment', 'Deployment'),
        ('other', 'Khác'),
    ], string='Phân loại tài liệu', default='user_manual', required=True)
    file = fields.Binary(string='Tệp đính kèm')
    file_name = fields.Char(string='Tên tệp')
    url = fields.Char(string='Đường dẫn (URL)')
    description = fields.Text(string='Mô tả')
    version = fields.Selection([
        ('12', 'Odoo 12'),
        ('13', 'Odoo 13'),
        ('14', 'Odoo 14'),
        ('15', 'Odoo 15'),
        ('16', 'Odoo 16'),
        ('17', 'Odoo 17'),
        ('18', 'Odoo 18'),
        ('19', 'Odoo 19'),
    ], string='Phiên bản áp dụng')
    sequence = fields.Integer(string='Thứ tự', default=10)
