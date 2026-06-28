# -*- coding: utf-8 -*-
{
    'name': 'DCG Master Data',
    'version': '18.0.1.0.0',
    'summary': 'Centralized master data for CRM, Contract, Project, Support and Finance',
    'description': """
DCG Master Data
===============

Module dữ liệu chủ (master data) dùng chung cho toàn bộ hệ thống DCG:

* Danh mục ngành nghề / nguồn khách hàng / dịch vụ
* Loại hợp đồng / phụ lục / nghiệm thu
* Loại ticket / mức độ / ưu tiên / SLA policy
* Loại chi phí / cost center
* KPI target / Alert rule

Phase 1: 14 model master data.
    """,
    'category': 'Tools',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
        'resource',
    ],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',

        # views - menu root
        'views/menu.xml',

        # views - CRM
        'views/customer_industry_views.xml',
        'views/customer_source_views.xml',
        'views/service_catalog_views.xml',

        # views - Contract
        'views/contract_type_views.xml',
        'views/contract_appendix_type_views.xml',
        'views/acceptance_type_views.xml',

        # views - Support
        'views/ticket_type_views.xml',
        'views/ticket_severity_views.xml',
        'views/ticket_priority_views.xml',
        'views/sla_policy_views.xml',

        # views - Finance
        'views/expense_type_views.xml',
        'views/cost_center_views.xml',

        # views - KPI & Alerts
        'views/kpi_target_views.xml',
        'views/alert_rule_views.xml',

        # seed data
        'data/master_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
