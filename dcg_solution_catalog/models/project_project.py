from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    solution_ids = fields.Many2many(
        comodel_name='solution.module',
        relation='project_project_solution_module_rel',
        column1='project_id',
        column2='solution_id',
        string='Giải pháp',
        domain="[('state', '=', 'ready')]",
    )

    def write(self, vals):
        added_ids_by_project = {}

        if 'solution_ids' in vals:
            for project in self:
                old_solution_ids = project.solution_ids.ids
                new_commands = vals['solution_ids']
                new_solution_ids = project._eval_solution_ids_commands(old_solution_ids, new_commands)

                # Cảnh báo loại bỏ giải pháp chỉ áp dụng khi không bị bỏ qua chủ động
                # (skip_solution_check dùng khi Project vừa được tạo từ CRM, hoặc khi
                # wizard cảnh báo đã được người dùng xác nhận).
                if not self.env.context.get('skip_solution_check'):
                    removed_ids = set(old_solution_ids) - set(new_solution_ids)
                    if removed_ids:
                        affected_tasks = self.env['project.task'].search([
                            ('project_id', '=', project.id),
                            ('solution_ids', 'in', list(removed_ids)),
                        ])
                        if affected_tasks:
                            wizard = self.env['project.solution.change.warning.wizard'].create({
                                'project_id': project.id,
                                'removed_solution_ids': [(6, 0, list(removed_ids))],
                                'new_solution_ids': [(6, 0, new_solution_ids)],
                                'affected_task_ids': [(6, 0, affected_tasks.ids)],
                            })
                            return {
                                'name': _('Cảnh Báo Thay Đổi Giải Pháp Dự Án'),
                                'type': 'ir.actions.act_window',
                                'res_model': 'project.solution.change.warning.wizard',
                                'res_id': wizard.id,
                                'view_mode': 'form',
                                'target': 'new',
                            }

                # Luôn ghi nhận giải pháp mới thêm (kể cả khi skip_solution_check=True)
                # để sinh Task ngay sau khi write() thành công bên dưới.
                added_ids_by_project[project.id] = set(new_solution_ids) - set(old_solution_ids)

        result = super().write(vals)

        # Sau khi giải pháp mới được gắn vào Project - dù qua CRM, qua wizard xác nhận
        # hay chỉnh sửa thủ công - tự sinh Task còn thiếu cho các Mẫu công việc tương ứng.
        for project in self:
            added_ids = added_ids_by_project.get(project.id)
            if added_ids:
                solutions = self.env['solution.module'].browse(list(added_ids))
                project._dcg_generate_tasks_from_solutions(solutions)

        return result

    def _eval_solution_ids_commands(self, current_ids, commands):
        result_set = set(current_ids)
        for cmd in commands:
            if isinstance(cmd, (list, tuple)):
                op = cmd[0]
                if op == 6:
                    result_set = set(cmd[2])
                elif op == 4:
                    result_set.add(cmd[1])
                elif op == 3:
                    result_set.discard(cmd[1])
                elif op == 5:
                    result_set.clear()
        return list(result_set)

    def _dcg_get_combined_skill_requirements(self, solution, task_template):
        """Gộp Yêu cầu kỹ năng của Module và của Mẫu công việc thành 1 danh sách duy nhất,
        theo từng kỹ năng (skill_id): nếu cùng 1 kỹ năng được khai báo ở cả 2 cấp, giá trị
        khai báo ở Mẫu công việc (cụ thể hơn) sẽ được ưu tiên/ghi đè giá trị ở Module (chung).

        :return: list[dict] các vals sẵn sàng để tạo ``project.task.skill.requirement``
            (chưa có ``task_id``, ``sequence`` giữ theo thứ tự Module trước, Mẫu công việc sau).
        """
        combined = {}
        for req in solution.skill_requirement_ids:
            combined[req.skill_id.id] = {
                'sequence': req.sequence,
                'skill_type_id': req.skill_type_id.id,
                'skill_id': req.skill_id.id,
                'skill_level_id': req.skill_level_id.id,
                'source_requirement_ref': 'solution.module.skill.requirement,%s' % req.id,
            }
        for req in task_template.skill_requirement_ids:
            combined[req.skill_id.id] = {
                'sequence': req.sequence,
                'skill_type_id': req.skill_type_id.id,
                'skill_id': req.skill_id.id,
                'skill_level_id': req.skill_level_id.id,
                'source_requirement_ref': 'solution.module.task.template.skill.requirement,%s' % req.id,
            }
        return list(combined.values())

    def _dcg_generate_tasks_from_solutions(self, solutions=None):
        """Tự sinh Task cho các Mẫu công việc (task template) của các Giải pháp/Module
        đã gắn vào Dự án, nếu Task tương ứng chưa tồn tại.

        - Dùng ``source_task_template_id`` để chống sinh trùng (thay vì so tên Task).
        - Task được tạo giữ liên kết với Module nguồn, Mẫu công việc nguồn và
          Cơ hội CRM nguồn (nếu Dự án được tạo từ CRM qua ``lead_id``).
        - Mỗi Task tự nhận luôn danh sách Yêu cầu kỹ năng (Kỹ năng + Mức tối thiểu) gộp từ
          Module và Mẫu công việc nguồn, để PM có sẵn thông tin phục vụ phân công nhân sự.

        :param solutions: tập ``solution.module`` cần xét; mặc định là toàn bộ
            ``solution_ids`` hiện có trên Dự án (dùng khi mới tạo Project từ CRM).
        """
        Task = self.env['project.task']
        TaskSkillRequirement = self.env['project.task.skill.requirement']

        for project in self:
            target_solutions = solutions if solutions is not None else project.solution_ids
            if not target_solutions:
                continue

            existing_template_ids = set(
                Task.search([
                    ('project_id', '=', project.id),
                    ('source_task_template_id', '!=', False),
                ]).mapped('source_task_template_id').ids
            )

            tasks_to_create = []
            skill_requirements_per_task = []
            for solution in target_solutions:
                for tmpl in solution.task_template_ids:
                    if tmpl.id in existing_template_ids:
                        continue
                    tasks_to_create.append({
                        'name': tmpl.name,
                        'description': tmpl.description,
                        'allocated_hours': tmpl.planned_hours,
                        'project_id': project.id,
                        'partner_id': project.partner_id.id if project.partner_id else False,
                        'solution_ids': [(6, 0, [solution.id])],
                        'source_module_id': solution.id,
                        'source_task_template_id': tmpl.id,
                        'source_lead_id': project.lead_id.id if project.lead_id else False,
                    })
                    skill_requirements_per_task.append(
                        self._dcg_get_combined_skill_requirements(solution, tmpl)
                    )
                    existing_template_ids.add(tmpl.id)

            if tasks_to_create:
                created_tasks = Task.create(tasks_to_create)
                skill_requirement_vals = []
                for task, skill_reqs in zip(created_tasks, skill_requirements_per_task):
                    for skill_req in skill_reqs:
                        skill_requirement_vals.append(dict(skill_req, task_id=task.id))
                if skill_requirement_vals:
                    TaskSkillRequirement.create(skill_requirement_vals)