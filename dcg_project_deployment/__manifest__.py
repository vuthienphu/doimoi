# -*- coding: utf-8 -*-
{
    'name': 'DCG - Thông tin triển khai dự án',
    'version': '19.0.1.0.0',
    'category': 'Dự án',
    'summary': 'Quản lý thông tin triển khai và vận hành dự án tại DCG',
    'description': """
        Lưu trữ tài khoản triển khai, thông tin kết nối máy chủ và ghi chú vận hành dự án.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/project_account_views.xml',
        'views/project_remote_views.xml',
        'views/project_project_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
