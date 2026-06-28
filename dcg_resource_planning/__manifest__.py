# -*- coding: utf-8 -*-
{
    'name': 'DCG Resource Planning',
    'version': '18.0.1.0.0',
    'summary': 'Capacity planning, resource allocation, forecast, utilization, bench',
    'description': """
DCG Resource Planning — PSA core
==================================

Quản lý capacity, allocation, forecast, utilization, bench cho nhân sự triển khai:

* Resource Role & Skill master (thay Selection, dùng chung CRM → Delivery → Finance)
* Resource Plan 1:1 với project — planned vs allocated vs actual
* Allocation theo % và giờ, validate over-allocation
* Resource Request từ PM → HR approve → allocate
* Capacity snapshot tháng (auto compute từ calendar + allocation)
* Forecast theo role/tháng — need vs current vs gap
* Utilization = billable / capacity
* Extend hr.employee: allocation summary, skill, bench

Flow: Estimate → Resource Request → Approve → Allocation → Timesheet → Variance → Finance.
    """,
    'category': 'Human Resources',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'hr',
        'resource',
        'dcg_master_data',
        'dcg_project_delivery',
        'dcg_timesheet_control',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/resource_role_views.xml',
        'views/resource_skill_views.xml',
        'views/resource_allocation_views.xml',
        'views/resource_request_views.xml',
        'views/resource_capacity_views.xml',
        'views/resource_forecast_views.xml',
        'views/resource_plan_views.xml',
        'views/hr_employee_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
