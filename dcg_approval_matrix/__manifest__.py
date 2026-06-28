# -*- coding: utf-8 -*-
{
    'name': 'DCG Approval Matrix',
    'version': '18.0.1.0.0',
    'summary': 'Generic approval matrix & approval engine for any business document',
    'description': """
DCG Approval Matrix
===================

Framework duyệt (approval engine) dùng chung cho mọi document nghiệp vụ DCG.

Tính năng phase 1:

* Cấu hình ma trận duyệt nhiều bước (matrix + line)
* Lọc step theo amount, company, department
* Approver theo: user cụ thể / group / quản lý trực tiếp của nhân viên
* Runtime: submit / approve / reject / cancel
* Snapshot step để audit và bảo vệ request khi matrix thay đổi
* Activity notification cho approver
* Callback approved / rejected / cancelled về document nguồn
* Mixin chuẩn để document nghiệp vụ kế thừa

Module này phụ thuộc dcg_master_data để dùng chung DCG category.
    """,
    'category': 'Tools',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
        'dcg_master_data',
    ],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',

        # data
        'data/ir_sequence_data.xml',

        # wizards
        'wizards/approval_reject_wizard_views.xml',
        'wizards/approval_cancel_wizard_views.xml',

        # views
        'views/menu.xml',
        'views/approval_matrix_views.xml',
        'views/approval_request_step_views.xml',
        'views/approval_log_views.xml',
        'views/approval_request_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
