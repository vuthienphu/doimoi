# -*- coding: utf-8 -*-
{
    'name': 'DCG Project Delivery',
    'version': '18.0.1.0.0',
    'summary': 'Project delivery management: scope, milestone, team, issue, change request',
    'description': """
DCG Project Delivery
=====================

Quản lý triển khai dự án sau khi có hợp đồng:

* Tạo project từ contract, map contract lines → project scope
* Quản lý scope / work package với progress tracking
* Milestone gắn payment schedule + acceptance
* Team assignment với role / allocation
* Issue / risk / blocker với health status tự tính
* Change request với impact analysis, button tạo contract appendix
* 8 trạng thái delivery: draft → ready → in_progress → on_hold → uat → done → closed

Flow: Contract → Project → Scope/Milestone/Team → Issue/Change → Acceptance/Done → Close.
    """,
    'category': 'Project',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'mail',
        'hr',
        'dcg_master_data',
        'dcg_contract_management',
    ],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # data
        'data/ir_sequence_data.xml',
        'data/task_stage_data.xml',
        # views — actions before menu
        'views/project_scope_views.xml',
        'views/project_milestone_views.xml',
        'views/project_member_views.xml',
        'views/project_issue_views.xml',
        'views/project_change_request_views.xml',
        'views/project_task_views.xml',
        'views/project_delivery_views.xml',
        'views/menu.xml',
        'views/contract_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
