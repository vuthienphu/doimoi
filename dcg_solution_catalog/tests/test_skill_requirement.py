from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSolutionModuleSkillRequirement(TransactionCase):
    """Kiểm tra luồng Yêu cầu kỹ năng: Danh mục -> Kỹ năng thuộc danh mục -> Mức tối thiểu theo danh mục."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.skill_type_backend = cls.env['hr.skill.type'].create({
            'name': 'DCG Backend',
            'skill_ids': [
                (0, 0, {'name': 'Odoo ORM'}),
                (0, 0, {'name': 'PostgreSQL'}),
            ],
            'skill_level_ids': [
                (0, 0, {'name': 'Cơ bản', 'level_progress': 25}),
                (0, 0, {'name': 'Thành thạo', 'level_progress': 100, 'default_level': True}),
            ],
        })
        cls.skill_type_pm = cls.env['hr.skill.type'].create({
            'name': 'DCG Quản lý dự án',
            'skill_ids': [
                (0, 0, {'name': 'Lập kế hoạch'}),
            ],
            'skill_level_ids': [
                (0, 0, {'name': 'Cơ bản', 'level_progress': 25}),
                (0, 0, {'name': 'Nâng cao', 'level_progress': 75}),
            ],
        })

        cls.skill_orm = cls.skill_type_backend.skill_ids.filtered(lambda skill: skill.name == 'Odoo ORM')
        cls.skill_planning = cls.skill_type_pm.skill_ids
        cls.level_backend_default = cls.skill_type_backend.skill_level_ids.filtered('default_level')
        cls.level_backend_basic = cls.skill_type_backend.skill_level_ids.filtered(lambda level: level.name == 'Cơ bản')
        cls.level_pm_basic = cls.skill_type_pm.skill_level_ids.filtered(lambda level: level.name == 'Cơ bản')

        cls.module = cls.env['solution.module'].create({
            'name': 'Module kiểm thử Yêu cầu kỹ năng',
            'code': 'test_skill_requirement',
            'version': '19',
            'state': 'ready',
        })

    def _new_requirement(self, **vals):
        return self.env['solution.module.skill.requirement'].new({
            'module_id': self.module.id,
            **vals,
        })

    def test_01_domains_filter_skills_and_levels_by_category(self):
        """Kỹ năng và mức tối thiểu đều bị lọc theo danh mục kỹ năng đang chọn."""
        model = self.env['solution.module.skill.requirement']
        expected_domain = "[('skill_type_id', '=', skill_type_id)]"
        self.assertEqual(model._fields['skill_id'].domain, expected_domain)
        self.assertEqual(model._fields['skill_level_id'].domain, expected_domain)

    def test_02_skill_dropdown_displays_category(self):
        """Bấm vào ô Kỹ năng: danh sách hiển thị kỹ năng kèm danh mục của kỹ năng đó."""
        view = self.env.ref('dcg_solution_catalog.solution_module_view_form')
        self.assertIn("'from_skill_dropdown': True", view.arch)
        self.assertEqual(
            self.skill_orm.with_context(from_skill_dropdown=True).display_name,
            'Odoo ORM (DCG Backend)',
        )

    def test_03_onchange_skill_id_syncs_category_and_level(self):
        """Chọn kỹ năng -> tự điền danh mục và mức tối thiểu mặc định của danh mục đó."""
        requirement = self._new_requirement()
        requirement.skill_id = self.skill_orm
        requirement._onchange_skill_id()
        self.assertEqual(requirement.skill_type_id, self.skill_type_backend)
        self.assertEqual(requirement.skill_level_id, self.level_backend_default)

    def test_04_onchange_skill_type_id_clears_unmatched_values(self):
        """Đổi danh mục -> bỏ kỹ năng và mức tối thiểu không thuộc danh mục mới."""
        requirement = self._new_requirement({
            'skill_type_id': self.skill_type_backend.id,
            'skill_id': self.skill_orm.id,
            'skill_level_id': self.level_backend_basic.id,
        })
        requirement.skill_type_id = self.skill_type_pm
        requirement._onchange_skill_type_id()
        self.assertFalse(requirement.skill_id)
        self.assertFalse(requirement.skill_level_id)

    def test_05_onchange_skill_type_id_keeps_matching_values(self):
        """Giữ nguyên kỹ năng và mức tối thiểu khi vẫn thuộc danh mục đang chọn."""
        requirement = self._new_requirement({
            'skill_type_id': self.skill_type_backend.id,
            'skill_id': self.skill_orm.id,
            'skill_level_id': self.level_backend_basic.id,
        })
        requirement._onchange_skill_type_id()
        self.assertEqual(requirement.skill_id, self.skill_orm)
        self.assertEqual(requirement.skill_level_id, self.level_backend_basic)

    def test_06_skill_must_belong_to_selected_category(self):
        """Không cho lưu kỹ năng không thuộc danh mục đã chọn."""
        with self.assertRaises(ValidationError):
            self.env['solution.module.skill.requirement'].create({
                'module_id': self.module.id,
                'skill_type_id': self.skill_type_backend.id,
                'skill_id': self.skill_planning.id,
                'skill_level_id': self.level_backend_basic.id,
            })

    def test_07_level_must_belong_to_selected_category(self):
        """Không cho lưu mức tối thiểu không thuộc danh mục đã chọn."""
        with self.assertRaises(ValidationError):
            self.env['solution.module.skill.requirement'].create({
                'module_id': self.module.id,
                'skill_type_id': self.skill_type_backend.id,
                'skill_id': self.skill_orm.id,
                'skill_level_id': self.level_pm_basic.id,
            })

    def test_08_create_valid_requirement(self):
        """Dữ liệu hợp lệ được lưu và hiển thị trong tab Yêu cầu kỹ năng của module."""
        requirement = self.env['solution.module.skill.requirement'].create({
            'module_id': self.module.id,
            'skill_type_id': self.skill_type_backend.id,
            'skill_id': self.skill_orm.id,
            'skill_level_id': self.level_backend_default.id,
        })
        self.assertIn(requirement, self.module.skill_requirement_ids)
