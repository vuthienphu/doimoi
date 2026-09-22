from odoo import api, models, fields


class SolutionModuleTaskTemplate(models.Model):
    _name = 'solution.module.task.template'
    _description = 'Mẫu công việc triển khai'
    _order = 'sequence, id'

    module_id = fields.Many2one('solution.module', string='Module giải pháp', ondelete='cascade', required=True)
    name = fields.Char(string='Tên công việc mẫu', required=True)
    description = fields.Text(string='Mô tả công việc')
    planned_hours = fields.Float(string='Thời gian ước tính (giờ)', default=1.0)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)

    skill_requirement_ids = fields.One2many(
        'solution.module.task.template.skill.requirement',
        'task_template_id',
        string='Yêu cầu kỹ năng',
    )
    skill_requirement_count = fields.Integer(
        string='Số yêu cầu kỹ năng',
        compute='_compute_skill_requirement_count',
    )

    @api.depends('skill_requirement_ids')
    def _compute_skill_requirement_count(self):
        for rec in self:
            rec.skill_requirement_count = len(rec.skill_requirement_ids)