# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_processing = fields.Boolean(string='Đang làm')
    is_test = fields.Boolean(string='Chuyển test')
    is_done = fields.Boolean(string='Hoàn thành')
    is_live = fields.Boolean(string='Đã đưa lên Live')
    is_dcg_default = fields.Boolean(string='Giai đoạn mặc định DCG')
    is_draft = fields.Boolean(string='Bản nháp')

    @api.model_create_multi
    def create(self, vals_list):
        stages = super().create(vals_list)
        dcg_stages = stages.filtered('is_dcg_default')
        projects = self.env['project.project'].with_context(active_test=False).search([])
        if projects and dcg_stages:
            dcg_stages.write({'project_ids': [(4, project.id) for project in projects]})
        return stages

    def unlink(self):
        if self.env.context.get('dcg_skip_stage_usage_check'):
            return super().unlink()
        used_stage = self.env['project.task'].search([('stage_id', 'in', self.ids)], limit=1).stage_id
        if used_stage:
            raise UserError(_('Stage đang được sử dụng.'))
        return super().unlink()

    @api.model
    def _dcg_cleanup_duplicate_stages(self):
        canonical_names = {
            'Cần làm': ['Cần làm'],
            'Đang làm': ['Đang làm', 'Đang thực hiện'],
            'Chuyển test': ['Chuyển test', 'Chờ kiểm tra'],
            'Hoàn thành': ['Hoàn thành'],
            'Đã đưa lên Live': ['Đã đưa lên Live'],
        }
        canonical_flags = {
            'Cần làm': {},
            'Đang làm': {'is_processing': True},
            'Chuyển test': {'is_test': True},
            'Hoàn thành': {'is_done': True},
            'Đã đưa lên Live': {'is_live': True},
        }

        for canonical_name, aliases in canonical_names.items():
            stages = self.with_context(active_test=False).search([('name', 'in', aliases)], order='id')
            if len(stages) <= 1:
                if stages:
                    stages.write({
                        'name': canonical_name,
                        'active': True,
                        'is_processing': canonical_flags[canonical_name].get('is_processing', False),
                        'is_test': canonical_flags[canonical_name].get('is_test', False),
                        'is_done': canonical_flags[canonical_name].get('is_done', False),
                        'is_live': canonical_flags[canonical_name].get('is_live', False),
                        'is_draft': canonical_name == 'Cần làm',
                        'is_dcg_default': True,
                    })
                continue

            canonical_stage = self._dcg_get_canonical_stage(canonical_name, stages)
            duplicate_stages = stages - canonical_stage
            projects = stages.mapped('project_ids')

            canonical_stage.write({
                'name': canonical_name,
                'active': True,
                'is_processing': canonical_flags[canonical_name].get('is_processing', False),
                'is_test': canonical_flags[canonical_name].get('is_test', False),
                'is_done': canonical_flags[canonical_name].get('is_done', False),
                'is_live': canonical_flags[canonical_name].get('is_live', False),
                'is_draft': canonical_name == 'Cần làm',
                'is_dcg_default': True,
                'project_ids': [(6, 0, projects.ids)],
            })

            self.env['project.task'].with_context(dcg_skip_stage_notification=True).search([
                ('stage_id', 'in', duplicate_stages.ids),
            ]).write({'stage_id': canonical_stage.id})

            duplicate_stages.with_context(dcg_skip_stage_usage_check=True).unlink()

    @api.model
    def _dcg_cleanup_non_standard_project_stages(self):
        standard_stages = self._dcg_standard_stages()
        todo_stage = self.env.ref('dcg_project_customize.task_stage_todo', raise_if_not_found=False)
        if not standard_stages or not todo_stage:
            return

        non_standard_stages = self.with_context(active_test=False).search([
            ('id', 'not in', standard_stages.ids),
        ])
        project_tasks = self.env['project.task'].with_context(dcg_skip_stage_notification=True).search([
            ('project_id', '!=', False),
            ('stage_id', 'in', non_standard_stages.ids),
        ])
        if project_tasks:
            project_tasks.write({'stage_id': todo_stage.id})

        stages_linked_to_projects = non_standard_stages.filtered('project_ids')
        if stages_linked_to_projects:
            stages_linked_to_projects.write({'project_ids': [(5, 0, 0)]})

    @api.model
    def _dcg_standard_stages(self):
        stages = self.env['project.task.type']
        for xmlid in (
            'dcg_project_customize.task_stage_todo',
            'dcg_project_customize.task_stage_processing',
            'dcg_project_customize.task_stage_testing',
            'dcg_project_customize.task_stage_done',
            'dcg_project_customize.task_stage_live',
        ):
            stage = self.env.ref(xmlid, raise_if_not_found=False)
            if stage:
                stages |= stage.with_context(active_test=False)
        return stages.sudo().sorted(lambda stage: (stage.sequence, stage.id))

    def _dcg_get_canonical_stage(self, canonical_name, stages):
        xmlid_by_name = {
            'Cần làm': 'dcg_project_customize.task_stage_todo',
            'Đang làm': 'dcg_project_customize.task_stage_processing',
            'Chuyển test': 'dcg_project_customize.task_stage_testing',
            'Hoàn thành': 'dcg_project_customize.task_stage_done',
            'Đã đưa lên Live': 'dcg_project_customize.task_stage_live',
        }
        xml_stage = self.env.ref(xmlid_by_name[canonical_name], raise_if_not_found=False)
        if xml_stage and xml_stage in stages:
            return xml_stage
        exact_stage = stages.filtered(lambda stage: stage.name == canonical_name)[:1]
        return exact_stage or stages[:1]
