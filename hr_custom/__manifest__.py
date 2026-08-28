# -*- coding: utf-8 -*-
{
    'name': 'Bravestars HR Custom',
    'version': '19.0.1.0.0',
    'category': 'Bravestars',
    'summary': 'Tùy chỉnh HR',
    'depends': ['hr', 'hr_level', 'hr_homeworking', 'om_hr_payroll', 'hr_org_chart'],
    'data': [
        'security/hr_groups.xml',
        'security/ir.model.access.csv',
        'views/hr_hospital_views.xml',
        'views/hr_contract_legal_entity_views.xml',
        'views/res_bank_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_employee_public_views.xml',
        'views/hr_department_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_custom/static/src/js/employee_public_open_guard.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
