# -*- coding: utf-8 -*-
{
    'name': 'DCG CRM Payment',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Chức năng quản lý và nhắc nhở thanh toán theo Cơ hội',
    'description': """
        Quản lý lịch sử thanh toán, theo dõi công nợ, nhắc nhở thanh toán định kỳ cho từng Cơ hội.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'mail',
        'dcg_crm_cost',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/cron_data.xml',
        'views/crm_payment_type_views.xml',
        'views/crm_lead_payment_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
