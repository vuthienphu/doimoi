# -*- coding: utf-8 -*-
{
    'name': 'DCG HR Resource',
    'version': '18.0.1.0.0',
    'summary': 'Delivery HR profile: career level, certificate, training, competency, KPI, availability',
    'description': """
DCG HR Resource — Năng lực nhân sự triển khai
===============================================

Mở rộng HR phục vụ Delivery, KHÔNG thay thế HR core (chấm công/nghỉ phép/lương):

* Career level (Intern → Fresher → Junior → Senior → Leader → Director)
* Certificate tracking (issue/expiry, attachment)
* Training history (course, result, provider)
* Competency assessment per period (technical, communication, leadership...)
* Delivery KPI per period (utilization, billable, customer score)
* Availability tracking (available/allocated/leave/training)
* Extend hr.employee: hour_cost, bill_rate, capacity, target_utilization

Tận dụng dcg.resource.role + dcg.resource.skill từ dcg_resource_planning (không tạo trùng).
    """,
    'category': 'Human Resources',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'dcg_master_data',
        'dcg_resource_planning',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/career_level_data.xml',
        'views/career_level_views.xml',
        'views/certificate_views.xml',
        'views/training_views.xml',
        'views/competency_views.xml',
        'views/kpi_views.xml',
        'views/availability_views.xml',
        'views/hr_employee_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
