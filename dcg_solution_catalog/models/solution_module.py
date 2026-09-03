from odoo import api, fields, models, _


class SolutionModule(models.Model):
    _name = 'solution.module'
    _description = 'Giải pháp Module Odoo'
    _order = 'name'

    name = fields.Char(string='Tên Module', required=True)
    code = fields.Char(string='Mã Module')
    solution_id = fields.Many2one('solution.solution', string='Giải pháp')
    configuration_id = fields.Many2one('solution.configuration', string='Cấu hình phân hệ')
    version = fields.Selection([
        ('12', 'Odoo 12'),
        ('13', 'Odoo 13'),
        ('14', 'Odoo 14'),
        ('15', 'Odoo 15'),
        ('16', 'Odoo 16'),
        ('17', 'Odoo 17'),
        ('18', 'Odoo 18'),
        ('19', 'Odoo 19'),
    ], string='Phiên bản Odoo', default='19', required=True)
    state = fields.Selection([
        ('draft', 'Bản thảo'),
        ('ready', 'Sẵn sàng triển khai'),
        ('deprecated', 'Ngưng sử dụng'),
    ], string='Trạng thái', default='draft', required=True)
    description = fields.Html(string='Mô tả & Phạm vi nghiệp vụ')
    active = fields.Boolean(string='Kích hoạt', default=True)

    feature_ids = fields.One2many('solution.module.feature', 'module_id', string='Chức năng')
    document_ids = fields.One2many('solution.module.document', 'module_id', string='Tài liệu')
    survey_checklist_ids = fields.One2many('solution.module.survey.checklist', 'module_id', string='Checklist khảo sát')
    implementation_checklist_ids = fields.One2many('solution.module.implementation.checklist', 'module_id', string='Checklist triển khai')
    handover_checklist_ids = fields.One2many('solution.module.handover.checklist', 'module_id', string='Checklist bàn giao')
    common_issue_ids = fields.One2many('solution.module.common.issue', 'module_id', string='Lỗi thường gặp')
    task_template_ids = fields.One2many('solution.module.task.template', 'module_id', string='Mẫu công việc')

    total_planned_hours = fields.Float(
        string='Tổng thời gian ước tính (giờ)',
        compute='_compute_total_planned_hours',
        store=True,
    )

    @api.depends('task_template_ids.planned_hours')
    def _compute_total_planned_hours(self):
        for rec in self:
            rec.total_planned_hours = sum(rec.task_template_ids.mapped('planned_hours'))
