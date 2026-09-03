# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Level',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Quản lý cấp bậc (Level) của nhân viên',
    'description': 'Thêm khái niệm Level cho nhân viên và ghép Level + Vị trí '
                   'công việc thành chức danh (job title).',
    'author': 'Bravestars',
    'license': 'LGPL-3',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_level_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
