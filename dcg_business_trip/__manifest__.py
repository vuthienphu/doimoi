# -*- coding: utf-8 -*-
{
    'name': 'DCG Business Trip',
    'version': '18.0.1.0.0',
    'summary': 'Business trip management: members, expenses, approval, finance sync',
    'description': """
DCG Business Trip
==================

Quản lý công tác / onsite triển khai, nguồn chi phí travel cho project finance:

* Đề nghị công tác với approval qua dcg_approval_matrix
* Quản lý thành viên chuyến đi (role, team lead)
* Chi phí estimated vs actual theo category (transport, hotel, allowance, meal...)
* Sync actual expense → project finance cost lines khi trip done
* Link project / contract / scope / milestone

Flow: Tạo Trip → Members + Estimated Expense → Submit Approval → Approved → In Progress →
      Actual Expense → Done → Sync to Finance.
    """,
    'category': 'Operations',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'hr',
        'dcg_master_data',
        'dcg_approval_matrix',
        'dcg_project_delivery',
        'dcg_project_finance',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/business_trip_member_views.xml',
        'views/business_trip_expense_views.xml',
        'views/business_trip_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
