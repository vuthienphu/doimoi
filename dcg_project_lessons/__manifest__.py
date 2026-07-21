# -*- coding: utf-8 -*-
{
    'name': 'DCG - Bài học kinh nghiệm dự án',
    'version': '19.0.1.0.0',
    'category': 'Dự án',
    'summary': 'Quản lý bài học kinh nghiệm của dự án tại DCG',
    'description': """
        Ghi nhận, xét duyệt và tái sử dụng bài học kinh nghiệm giữa các dự án DCG.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'mail',
    ],
    'data': [
        'security/security_groups.xml',
        'data/default_user_access.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'wizard/project_lesson_archive_warning_views.xml',
        'views/project_lesson_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/project_milestone_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
