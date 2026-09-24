from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    solution_ids = fields.Many2many(
        comodel_name='solution.module',
        relation='project_task_solution_module_rel',
        column1='task_id',
        column2='solution_id',
        string='Giải pháp',
    )

    source_module_id = fields.Many2one(
        'solution.module',
        string='Module nguồn',
        readonly=True,
        copy=False,
        index=True,
        help='Module giải pháp mà Task này được tự động sinh ra. '
             'Rỗng nếu Task được tạo thủ công.',
    )
    source_task_template_id = fields.Many2one(
        'solution.module.task.template',
        string='Mẫu công việc nguồn',
        readonly=True,
        copy=False,
        index=True,
        ondelete='set null',
        help='Mẫu công việc (Task Template) mà Task này được tự động sinh ra. '
             'Dùng để chống sinh trùng Task khi đồng bộ lại giải pháp.',
    )
    source_lead_id = fields.Many2one(
        'crm.lead',
        string='Cơ hội nguồn',
        readonly=True,
        copy=False,
        index=True,
        help='Cơ hội CRM đã tạo ra Dự án (và do đó gián tiếp tạo ra Task này), '
             'nếu Dự án được tạo tự động từ CRM.',
    )
    is_auto_generated = fields.Boolean(
        string='Task tự động sinh',
        compute='_compute_is_auto_generated',
        store=True,
        help='True nếu Task được hệ thống tự sinh từ Mẫu công việc của giải pháp.',
    )
    skill_requirement_ids = fields.One2many(
        'project.task.skill.requirement',
        'task_id',
        string='Yêu cầu kỹ năng',
        help='Danh sách Kỹ năng + Mức tối thiểu cần có để thực hiện Task này, dùng để đối chiếu '
             'khi phân công nhân sự. Với Task tự sinh, danh sách này được tự động điền từ '
             'Mẫu công việc/Module nguồn; PM vẫn có thể thêm/sửa/xóa riêng cho Task này.',
    )

    @api.depends('source_task_template_id')
    def _compute_is_auto_generated(self):
        for task in self:
            task.is_auto_generated = bool(task.source_task_template_id)

    @api.onchange('project_id')
    def _onchange_project_id_solution(self):
        if self.project_id and self.project_id.solution_ids:
            self.solution_ids = [(6, 0, self.project_id.solution_ids.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'project_id' in vals and 'solution_ids' not in vals:
                project = self.env['project.project'].browse(vals['project_id'])
                if project.exists() and project.solution_ids:
                    vals['solution_ids'] = [(6, 0, project.solution_ids.ids)]

            # Task KHÔNG đi qua luồng tự sinh từ Mẫu công việc (project._dcg_generate_tasks_from_solutions
            # không truyền source_task_template_id) -- tức là Task được tạo thủ công ngay trong Dự án,
            # nhưng có gắn Module (solution_ids, tự điền ở trên hoặc do người dùng chọn tay).
            # Trường hợp này vẫn phải tự nhận Yêu cầu kỹ năng, lấy MẶC ĐỊNH từ Module vì không có
            # Mẫu công việc nào để tham chiếu.
            if not vals.get('source_task_template_id') and 'skill_requirement_ids' not in vals:
                module_ids = self._dcg_eval_m2m_commands([], vals.get('solution_ids') or [])
                if module_ids:
                    modules = self.env['solution.module'].browse(module_ids)
                    default_reqs = self.env['project.project']._dcg_get_combined_skill_requirements(
                        modules, self.env['solution.module.task.template']
                    )
                    if default_reqs:
                        vals['skill_requirement_ids'] = [(0, 0, req) for req in default_reqs]
        return super().create(vals_list)

    def write(self, vals):
        """Khi Module (solution_ids) được gắn THÊM vào 1 Task đã tồn tại (không qua luồng sinh từ
        Mẫu công việc), tự bổ sung Yêu cầu kỹ năng mặc định của Module đó nếu Task chưa có sẵn kỹ
        năng cùng tên -- cùng nguyên tắc với lúc tạo mới ở ``create()``.
        """
        added_module_ids_by_task = {}
        if 'solution_ids' in vals:
            for task in self:
                if task.source_task_template_id:
                    # Task theo Mẫu công việc: việc đồng bộ kỹ năng do project._dcg_generate_tasks_from_solutions
                    # và nút "Đồng bộ lại Yêu cầu kỹ năng" quản lý, tránh chồng lấn ở đây.
                    continue
                new_module_ids = set(self._dcg_eval_m2m_commands(task.solution_ids.ids, vals['solution_ids']))
                added = new_module_ids - set(task.solution_ids.ids)
                if added:
                    added_module_ids_by_task[task.id] = added

        result = super().write(vals)

        for task in self:
            added = added_module_ids_by_task.get(task.id)
            if not added:
                continue
            modules = self.env['solution.module'].browse(list(added))
            existing_skill_ids = set(task.skill_requirement_ids.mapped('skill_id').ids)
            default_reqs = self.env['project.project']._dcg_get_combined_skill_requirements(
                modules, self.env['solution.module.task.template']
            )
            vals_to_create = [
                dict(req, task_id=task.id)
                for req in default_reqs
                if req['skill_id'] not in existing_skill_ids
            ]
            if vals_to_create:
                self.env['project.task.skill.requirement'].create(vals_to_create)

        return result

    @api.model
    def _dcg_eval_m2m_commands(self, old_ids, commands):
        """Tính danh sách id cuối cùng của 1 field Many2many sau khi áp dụng chuỗi lệnh ORM
        (tuple (6,0,ids)/(4,id)/(3,id)/(2,id)/(5,0,0), hoặc danh sách id thuần theo API mới).
        Dùng để đọc trước nội dung ``vals['solution_ids']`` trong ``create()``/``write()`` mà
        không cần đợi bản ghi được lưu xuống DB.
        """
        result_set = set(old_ids)
        if not commands:
            return list(result_set)
        for cmd in commands:
            if isinstance(cmd, (list, tuple)):
                op = cmd[0]
                if op == 6:
                    result_set = set(cmd[2])
                elif op == 4:
                    result_set.add(cmd[1])
                elif op in (2, 3):
                    result_set.discard(cmd[1])
                elif op == 5:
                    result_set.clear()
                # op == 0 (tạo mới bản ghi liên kết): chưa có id sẵn nên bỏ qua.
            elif isinstance(cmd, int):
                result_set.add(cmd)
        return list(result_set)

    def action_dcg_resync_skill_requirements(self):
        """Đồng bộ lại Yêu cầu kỹ năng từ Module/Mẫu công việc nguồn cho các Task đã tồn tại.

        Cần dùng khi:
        - Task được tạo TRƯỚC KHI tính năng tự nhận Yêu cầu kỹ năng được cài đặt, nên
          ``skill_requirement_ids`` đang trống dù Template/Module đã có khai báo.
        - Module/Mẫu công việc vừa được cập nhật thêm/sửa Yêu cầu kỹ năng SAU KHI Task đã sinh ra,
          và bạn muốn Task nhận thêm các kỹ năng mới đó.

        Chỉ bổ sung các kỹ năng còn THIẾU trên Task (so theo ``skill_id``), không đụng tới hoặc
        xóa các dòng PM đã tự thêm/sửa riêng cho Task.
        """
        SkillRequirement = self.env['project.task.skill.requirement']
        ProjectProject = self.env['project.project']
        vals_to_create = []

        for task in self:
            if not task.source_task_template_id:
                continue
            combined = ProjectProject._dcg_get_combined_skill_requirements(
                task.source_module_id, task.source_task_template_id
            )
            existing_skill_ids = set(task.skill_requirement_ids.mapped('skill_id').ids)
            for req in combined:
                if req['skill_id'] not in existing_skill_ids:
                    vals_to_create.append(dict(req, task_id=task.id))

        if vals_to_create:
            SkillRequirement.create(vals_to_create)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Đồng bộ Yêu cầu kỹ năng'),
                'message': _('Đã bổ sung %(count)s dòng yêu cầu kỹ năng còn thiếu.', count=len(vals_to_create))
                    if vals_to_create else _('Không có yêu cầu kỹ năng nào cần bổ sung thêm.'),
                'type': 'success' if vals_to_create else 'info',
                'sticky': False,
            },
        }