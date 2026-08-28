# -*- coding: utf-8 -*-
{
    'name': 'Dcg Login Custom',
    'version': '1.0',
    'summary': 'Remove unnecessary elements from the login page',
    'depends': ['web', 'auth_signup', 'auth_oauth', 'hr'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/login.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
