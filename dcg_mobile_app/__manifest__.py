# -*- coding: utf-8 -*-
{
    'name': 'DCG Mobile App Connector & Push Notifications',
    'version': '1.0.0',
    'summary': 'Quản lý xác thực Google Login cho Mobile App, Token thiết bị, Lịch sử đăng nhập & Push Notification Firebase FCM',
    'description': """
        Module tích hợp dành cho Mobile App:
        - API Xác thực đăng nhập Google (chặn email ngoài hệ thống).
        - Quản lý Device Token (Firebase Cloud Messaging).
        - Ghi vết lịch sử đăng nhập trên các thiết bị.
        - Dịch vụ gửi Push Notification tới Mobile App.
        - Cấu hình Firebase FCM trong System Parameters.
    """,
    'category': 'Mobile',
    'author': 'DCG Team',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'views/mobile_device_token_views.xml',
        'views/mobile_login_history_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
