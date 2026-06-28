# -*- coding: utf-8 -*-
{
    'name': 'DCG Timesheet Control',
    'version': '18.0.1.0.0',
    'summary': 'Timesheet sheets, approval, billable/OT tracking, project actual sync',
    'description': """
DCG Timesheet Control
======================

Quản lý ghi nhận công, kiểm soát effort, billable/non-billable, OT và approval:

* Timesheet Sheet theo kỳ (tuần/tháng) cho mỗi nhân sự
* Mở rộng account.analytic.line với project delivery, scope, charge_type, OT
* OT Request với approval riêng
* Auto sync actual hours → project scope / project delivery
* Costing fields (cost_rate, billing_rate) chuẩn bị cho project finance

Flow: Ghi line hằng ngày → Gom vào Sheet → Submit → Approve → Actual cập nhật Project.
    """,
    'category': 'Human Resources/Timesheets',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'hr_timesheet',
        'mail',
        'hr',
        'project',
        'dcg_master_data',
        'dcg_project_delivery',
    ],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # data
        'data/ir_sequence_data.xml',
        # wizard
        'wizard/generate_sheet_wizard_views.xml',
        # views
        'views/timesheet_sheet_views.xml',
        'views/account_analytic_line_views.xml',
        'views/timesheet_ot_request_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
