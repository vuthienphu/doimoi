# -*- coding: utf-8 -*-
{
    'name': 'DCG Project Finance',
    'version': '18.0.1.0.0',
    'summary': 'Project P&L, budget vs actual, cost/revenue tracking, finance health',
    'description': """
DCG Project Finance
====================

Lớp tài chính dự án — tổng hợp planned/actual revenue, cost, margin, collection:

* Finance header 1:1 với project delivery
* Cost lines: labor (từ timesheet), travel, subcontract, manual
* Revenue lines: từ contract payment schedule, appendix, manual
* Planned vs Actual variance, finance health auto-compute
* Collection tracking (invoiced / collected / outstanding)

Flow: Contract/Estimate → Finance Snapshot → Timesheet Actual Cost → Payment/Invoice →
      P&L Summary → Variance Alert → Close.
    """,
    'category': 'Project',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'hr',
        'dcg_contract_management',
        'dcg_project_delivery',
        'dcg_timesheet_control',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/project_finance_cost_line_views.xml',
        'views/project_finance_revenue_line_views.xml',
        'views/project_finance_views.xml',
        'views/menu.xml',
        'views/contract_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
