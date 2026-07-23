# -*- coding: utf-8 -*-
{
    'name': 'DCG CRM Cost',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Quản lý chi phí thực tế theo Cơ hội',
    'description': """
        Thêm tính năng theo dõi chi phí thực tế phát sinh của từng Cơ hội, tự động tính toán lãi/lỗ và hiển thị báo cáo.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'mail',
        'dcg_crm_estimation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_cost_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
