{
    'name': 'Hệ thống Yêu cầu Khách hàng & Quản lý Task',
    'version': '19.0.2.0.0',
    'license': 'LGPL-3',
    'summary': 'Hệ thống tiếp nhận Yêu cầu Khách hàng (Web/Zalo/Nội bộ) và Quản lý Task Dự án',
    'author': 'Ahkio Consulting Oy',
    'website': 'https://www.ahkio.com',
    'category': 'Services',
    'images': ['static/description/banner.jpg'],
    'depends': [
        'project',
        'website',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'views/helpdesk_ticket_views.xml',
        'views/project_task_views.xml',
        'views/res_partner_views.xml',
        'views/res_partner_zalo_channel_views.xml',
        'views/customer_request_templates.xml',
        'views/menu_views.xml',
        'wizard/helpdesk_ticket_create_task_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dcg_helpdesk_project/static/src/css/dashboard.css',
            'dcg_helpdesk_project/static/src/js/dashboard.js',
            'dcg_helpdesk_project/static/src/xml/dashboard_templates.xml',
        ],
        'web.assets_frontend': [
            'dcg_helpdesk_project/static/src/css/customer_request.css',
        ],
    },
    'installable': True,
    'application': True,
}
