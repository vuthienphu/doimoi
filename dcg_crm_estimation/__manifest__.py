# -*- coding: utf-8 -*-
{
    'name': 'DCG CRM Estimation',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Ước tính giá trị dự án Presales',
    'description': """
        Thêm tính năng lập bảng ước tính số man-day và các chi phí khác cho dự án, tính toán tự động giá vốn nhân sự, tổng vốn, lợi nhuận và biên lợi nhuận (margin) trước khi báo giá.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'mail',
        'dcg_custom_crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_role_cost_data.xml',
        'views/crm_role_cost_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
