# -*- coding: utf-8 -*-
{
    'name': 'DCG Project Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Project management dashboard for DCG',
    'description': """
        Dashboard quản trị dự án theo đặc tả Phần B: KPI, tiến độ dự án,
        phân bố Task theo Stage, xu hướng, workload và các danh sách theo dõi.
    """,
    'author': 'DM Group',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'web',
        'dcg_project_customize',
    ],
    'data': [
        'security/security.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dcg_project_dashboard/static/src/js/project_dashboard.js',
            'dcg_project_dashboard/static/src/xml/project_dashboard.xml',
            'dcg_project_dashboard/static/src/css/project_dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
