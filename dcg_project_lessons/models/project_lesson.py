# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _


class ProjectLesson(models.Model):
    _name = 'project.lesson'
    _description = 'Bài học kinh nghiệm dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    project_id = fields.Many2one('project.project', string='Dự án', required=True, tracking=True, ondelete='cascade')
    name = fields.Char(string='Tiêu đề', required=True, size=256, tracking=True)
    category = fields.Selection([
        ('business', 'Nghiệp vụ'),
        ('technical', 'Kỹ thuật'),
        ('infrastructure', 'Hạ tầng'),
        ('deployment', 'Triển khai'),
        ('performance', 'Hiệu năng'),
        ('security', 'Bảo mật'),
        ('testing', 'Kiểm thử'),
        ('training', 'Đào tạo'),
        ('customer', 'Khách hàng'),
        ('other', 'Khác'),
    ], string='Phân loại', required=True, tracking=True)
    module = fields.Char(string='Phân hệ Odoo')
    task_id = fields.Many2one('project.task', string='Công việc')
    milestone_id = fields.Many2one('project.milestone', string='Mốc dự án')
    priority = fields.Selection([
        ('0', 'Bình thường'),
        ('1', 'Quan trọng'),
        ('2', 'Nghiêm trọng'),
    ], string='Mức độ ưu tiên', default='0', tracking=True)
    problem = fields.Text(string='Vấn đề', required=True)
    cause = fields.Text(string='Nguyên nhân gốc rễ')
    solution = fields.Text(string='Giải pháp')
    result = fields.Text(string='Kết quả')
    recommendation = fields.Text(string='Khuyến nghị')
    tag_ids = fields.Many2many('project.tags', string='Thẻ')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'project_lesson_ir_attachment_rel',
        'lesson_id',
        'attachment_id',
        string='Tệp đính kèm',
    )
    author_id = fields.Many2one(
        'res.users',
        string='Người ghi nhận',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    date = fields.Date(string='Ngày ghi nhận', default=fields.Date.context_today, tracking=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('archived', 'Đã lưu trữ'),
    ], string='Trạng thái', default='draft', tracking=True)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            return {
                'domain': {
                    'task_id': [('project_id', '=', self.project_id.id)],
                    'milestone_id': [('project_id', '=', self.project_id.id)],
                },
            }
        return {'domain': {'task_id': [], 'milestone_id': []}}

    @api.onchange('task_id')
    def _onchange_task_id(self):
        if self.task_id and not self.project_id:
            self.project_id = self.task_id.project_id
        if self.task_id and self.task_id.project_id != self.project_id:
            self.task_id = False

    @api.onchange('milestone_id')
    def _onchange_milestone_id(self):
        if self.milestone_id and not self.project_id:
            self.project_id = self.milestone_id.project_id
        if self.milestone_id and self.milestone_id.project_id != self.project_id:
            self.milestone_id = False

    @api.constrains('project_id', 'task_id', 'milestone_id')
    def _check_related_records_project(self):
        for lesson in self:
            if lesson.task_id and lesson.task_id.project_id != lesson.project_id:
                raise ValidationError(_('Công việc đã chọn phải thuộc dự án của bài học.'))
            if lesson.milestone_id and lesson.milestone_id.project_id != lesson.project_id:
                raise ValidationError(_('Mốc dự án đã chọn phải thuộc dự án của bài học.'))

    def _check_pm_access(self):
        if not (
            self.env.user.has_group('dcg_project_lessons.group_project_lesson_pm')
            or self.env.user.has_group('dcg_project_lessons.group_project_lesson_director')
            or self.env.user.has_group('base.group_system')
        ):
            raise AccessError(_('Chỉ Quản lý dự án hoặc Giám đốc được thực hiện thao tác này.'))

    def action_confirm(self):
        self._check_pm_access()
        invalid = self.filtered(lambda lesson: lesson.state != 'draft')
        if invalid:
            raise UserError(_('Chỉ có thể xác nhận bài học đang ở trạng thái Nháp.'))
        self.write({'state': 'confirmed'})

    def action_archive_lesson(self):
        self._check_pm_access()
        invalid = self.filtered(lambda lesson: lesson.state == 'archived')
        if invalid:
            raise UserError(_('Các bài học đã chọn đã được lưu trữ.'))
        self.write({'state': 'archived'})

    def action_unarchive_lesson(self):
        self._check_pm_access()
        self.write({'state': 'draft'})

    def unlink(self):
        if any(lesson.state != 'archived' for lesson in self):
            raise UserError(_('Chỉ có thể xóa bài học đã được lưu trữ.'))
        return super().unlink()
