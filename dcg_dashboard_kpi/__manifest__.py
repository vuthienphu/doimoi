# -*- coding: utf-8 -*-
{
    'name': 'DCG Dashboard KPI',
    'version': '18.0.1.0.0',
    'summary': 'Executive dashboard, KPI, drill-down — OWL + Chart.js',
    'description': """
DCG Dashboard KPI — Presentation Layer
========================================

Dashboard điều hành cho Ban Giám đốc & Manager, tổng hợp dữ liệu từ toàn bộ hệ thống:

* Executive: Revenue, Profit, Margin, Project Status, Resource
* Delivery: Project Progress, Milestone, Issue, Budget vs Actual
* Finance: Revenue Trend, Cost Breakdown, Collection, Margin
* Support: Open Tickets, SLA, Critical, Response Time

Kiến trúc: ir.actions.client → OWL Component → RPC → Python Service → JSON → Chart.js.
Không ghi dữ liệu, chỉ đọc. Drill-down mở Action Odoo chuẩn.
    """,
    'category': 'Reporting',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'web',
        'dcg_master_data',
        'dcg_crm_presales',
        'dcg_contract_management',
        'dcg_project_delivery',
        'dcg_timesheet_control',
        'dcg_project_finance',
        'dcg_helpdesk_warranty',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/dashboard_actions.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dcg_dashboard_kpi/static/src/scss/dashboard.scss',
            'dcg_dashboard_kpi/static/src/xml/widgets/*.xml',
            'dcg_dashboard_kpi/static/src/xml/*.xml',
            'dcg_dashboard_kpi/static/src/js/widgets/*.js',
            'dcg_dashboard_kpi/static/src/js/*.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
