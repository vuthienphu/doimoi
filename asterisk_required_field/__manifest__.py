# -*- coding: utf-8 -*-
{
    'name': 'Asterisk on Required Fields',
    'version': '1.0',
    'summary': 'Thêm dấu * vào cuối nhãn của các field required trên form view',
    'description': """
Đánh dấu field required trên form view
======================================

Tự động thêm dấu ``*`` vào cuối nhãn (label) của mọi field đang ở trạng thái
bắt buộc trên **form view** — dù required được khai báo trong Python
(``required=True``) hay do một điều kiện required trên XML được thỏa mãn.

Áp dụng toàn hệ thống bằng cách patch component ``FormLabel`` (vốn chỉ dùng cho
form view), nên không cần khai báo gì thêm trên từng view.
""",
    'category': 'Technical',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'asterisk_required_field/static/src/form_label_asterisk.js',
            'asterisk_required_field/static/src/form_label_asterisk.xml',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
