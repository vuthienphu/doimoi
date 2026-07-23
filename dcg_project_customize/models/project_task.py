# -*- coding: utf-8 -*-

from email.utils import formataddr

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    reviewer_ids = fields.Many2many(
        'res.users',
        'project_task_reviewer_rel',
        'task_id',
        'user_id',
        string='Danh sách người kiểm tra',
    )
    planned_finish_date = fields.Datetime(string='Thời gian dự kiến hoàn thành')
    actual_finish_date = fields.Datetime(string='Thời gian thực tế hoàn thành')
    checklist_ids = fields.One2many(
        'task.checklist',
        'task_id',
        string='Danh sách checklist',
    )

    def action_open_subtasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Công việc con',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
                'default_project_id': self.project_id.id,
            },
        }

    def write(self, vals):
        result = super().write(vals)
        if 'stage_id' in vals and not self.env.context.get('dcg_skip_stage_notification'):
            for task in self:
                task._send_stage_notification()
        return result

    def _send_stage_notification(self):
        self.ensure_one()
        stage = self.stage_id
        if stage.is_processing:
            self._send_mail_processing()
        elif stage.is_test:
            self._send_mail_test()
        elif stage.is_done:
            self._send_mail_done()

    def _send_mail_processing(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_processing_notify',
            self.create_uid,
        )

    def _send_mail_test(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_test_notify',
            self.reviewer_ids,
        )

    def _send_mail_done(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_done_notify',
            self.create_uid | self.user_ids,
        )

    def _send_reminder_processing(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_reminder_processing',
            self.create_uid | self.user_ids,
        )

    def _send_reminder_test(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_reminder_test',
            self.create_uid | self.user_ids | self.reviewer_ids,
        )

    def _send_reminder_done_not_live(self):
        self.ensure_one()
        self._send_task_template(
            'dcg_project_customize.task_reminder_done_not_live',
            self.create_uid | self.user_ids,
        )

    def _send_task_template(self, template_xmlid, users):
        self.ensure_one()
        emails = list(dict.fromkeys(users.filtered(lambda user: user.email).mapped('email')))
        if not emails:
            return False

        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return False

        return template.send_mail(
            self.id,
            force_send=True,
            email_values={'email_to': ','.join(emails)},
        )

    def _get_task_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return '%s/web#id=%s&model=project.task&view_type=form' % (base_url, self.id)

    def _get_mail_from(self):
        self.ensure_one()
        config = self.env['ir.config_parameter'].sudo()
        company = self.env.company
        email = (
            config.get_param('dcg_project_customize.mail_from')
            or company.email
            or self.env.user.email
        )
        if not email:
            return ''

        name = (
            config.get_param('dcg_project_customize.mail_from_name')
            or company.name
            or self.env.user.name
        )
        return formataddr((name, email)) if name else email

    @api.model
    def _cron_send_daily_reminders(self):
        processing = self.search([('stage_id.is_processing', '=', True)])
        for task in processing:
            task._send_reminder_processing()

        testing = self.search([('stage_id.is_test', '=', True)])
        for task in testing:
            task._send_reminder_test()

        done_not_live = self.search([
            ('stage_id.is_done', '=', True),
            ('stage_id.is_live', '=', False),
        ])
        for task in done_not_live:
            task._send_reminder_done_not_live()
