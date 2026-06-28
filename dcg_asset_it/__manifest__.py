# -*- coding: utf-8 -*-
{
    'name': 'DCG Asset IT',
    'version': '18.0.1.0.0',
    'summary': 'IT & project asset management: device, license, assignment, warranty, maintenance',
    'description': """
DCG Asset IT — Quản trị tài sản CNTT & triển khai
====================================================

Quản lý vòng đời tài sản phục vụ triển khai dự án (không thay thế Asset Accounting):

* Asset register: laptop, server, thiết bị mạng, phần mềm, cloud...
* Dynamic stage workflow (New → In Stock → Assigned → Maintenance → Retired → Disposed)
* Assignment dài hạn (nhân viên/dự án) + Checkout mượn tạm
* Warranty tracking + maintenance log
* License management (seat count, expiry)
* Software install tracking per device
* Location management (kho, văn phòng, server room, khách hàng)
* History audit trail

Flow: Purchase → Register → Assign → Use → Maintenance → Return → Retire.
    """,
    'category': 'Operations',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'hr',
        'dcg_master_data',
        'dcg_project_delivery',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/asset_stage_data.xml',
        'views/asset_type_views.xml',
        'views/asset_category_views.xml',
        'views/asset_stage_views.xml',
        'views/asset_location_views.xml',
        'views/asset_assignment_views.xml',
        'views/asset_warranty_views.xml',
        'views/asset_maintenance_views.xml',
        'views/asset_license_views.xml',
        'views/asset_checkout_views.xml',
        'views/asset_views.xml',
        'views/hr_employee_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
