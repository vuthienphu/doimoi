# -*- coding: utf-8 -*-
{
    'name': 'DCG Project Customize',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Customize Project and Task workflow for DCG',
    'description': """
        Customize Project creation from CRM opportunities, task reviewers,
        checklists, stage notifications, and daily task reminders.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'crm',
        'mail',
        'hr',
        'survey',
        'hr_timesheet',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/cron_data.xml',
        'data/stage_data.xml',
        'views/crm_lead_views.xml',
        'views/project_project_views.xml',
        'views/project_project_stage_views.xml',
        'views/project_task_type_views.xml',
        'views/project_task_views.xml',
        'views/project_task_time_tracking_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
