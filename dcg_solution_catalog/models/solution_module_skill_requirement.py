from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SolutionModuleSkillRequirement(models.Model):
    _name = 'solution.module.skill.requirement'
    _description = 'Yêu cầu kỹ năng của Module'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    module_id = fields.Many2one(
        'solution.module',
        string='Module',
        required=True,
        ondelete='cascade',
    )
    skill_type_id = fields.Many2one(
        'hr.skill.type',
        string='Danh mục kỹ năng',
        required=True,
        index=True,
        default=lambda self: self.env['hr.skill.type'].search([], limit=1),
        help='Chọn danh mục kỹ năng để lọc danh sách kỹ năng bên dưới.',
    )
    skill_id = fields.Many2one(
        'hr.skill',
        string='Kỹ năng',
        required=True,
        index=True,
        domain="[('skill_type_id', '=', skill_type_id)]",
        help='Chỉ hiển thị kỹ năng thuộc danh mục đã chọn. Khi bấm vào ô này, mỗi kỹ năng được hiển thị '
             'kèm danh mục của nó và danh mục sẽ tự cập nhật theo kỹ năng được chọn.',
    )
    skill_level_id = fields.Many2one(
        'hr.skill.level',
        string='Mức tối thiểu',
        required=True,
        index=True,
        domain="[('skill_type_id', '=', skill_type_id)]",
        help='Danh sách mức tối thiểu phụ thuộc vào danh mục kỹ năng đã chọn ở kỹ năng.',
    )

    @api.model
    def _dcg_get_default_skill_level(self, skill_type):
        """Mức tối thiểu mặc định của danh mục: ưu tiên mức có cờ 'Mặc định', nếu không lấy mức đầu tiên."""
        levels = skill_type.skill_level_ids
        return (levels.filtered('default_level') or levels)[:1]

    @api.onchange('skill_id')
    def _onchange_skill_id(self):
        """Chọn kỹ năng -> hiển thị/đồng bộ danh mục của kỹ năng đó và lọc lại mức tối thiểu theo danh mục."""
        if not self.skill_id:
            self.skill_level_id = False
            return
        skill_type = self.skill_id.skill_type_id
        if self.skill_type_id != skill_type:
            self.skill_type_id = skill_type
        if not self.skill_level_id or self.skill_level_id.skill_type_id != skill_type:
            self.skill_level_id = self._dcg_get_default_skill_level(skill_type)

    @api.onchange('skill_type_id')
    def _onchange_skill_type_id(self):
        """Đổi danh mục -> bỏ kỹ năng và mức tối thiểu không còn thuộc danh mục mới."""
        if self.skill_id and self.skill_id.skill_type_id != self.skill_type_id:
            self.skill_id = False
        if self.skill_level_id and self.skill_level_id.skill_type_id != self.skill_type_id:
            self.skill_level_id = False

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        """Kỹ năng phải thuộc danh mục kỹ năng đã chọn."""
        for record in self:
            if not record.skill_id or not record.skill_type_id:
                continue
            if record.skill_id.skill_type_id != record.skill_type_id:
                raise ValidationError(_(
                    'Kỹ năng "%(skill)s" không thuộc danh mục kỹ năng "%(skill_type)s".',
                    skill=record.skill_id.name,
                    skill_type=record.skill_type_id.name,
                ))

    @api.constrains('skill_level_id', 'skill_type_id')
    def _check_skill_level(self):
        """Mức tối thiểu phải thuộc danh mục kỹ năng đã chọn."""
        for record in self:
            if not record.skill_level_id or not record.skill_type_id:
                continue
            if record.skill_level_id.skill_type_id != record.skill_type_id:
                raise ValidationError(_(
                    'Mức tối thiểu "%(level)s" không thuộc danh mục kỹ năng "%(skill_type)s".',
                    level=record.skill_level_id.name,
                    skill_type=record.skill_type_id.name,
                ))
