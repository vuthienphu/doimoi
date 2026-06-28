# -*- coding: utf-8 -*-
{
    'name': 'DCG Helpdesk Warranty',
    'version': '18.0.1.0.0',
    'summary': 'Post-delivery warranty tickets, SLA, team, knowledge base',
    'description': """
DCG Helpdesk Warranty
======================

Hệ thống quản lý bảo hành & hỗ trợ sau triển khai — module cuối cùng trong lifecycle dự án:

* Ticket với dynamic stage (kanban drag & drop)
* Multi-tag phân loại đa chiều (module, technology, business)
* Team support với leader/members
* SLA policy theo severity × priority
* Activity timeline xử lý ticket
* Solution / Knowledge base
* Warranty status auto-compute từ contract dates
* Tích hợp project, contract, timesheet

Flow: Contract Go-live → Warranty Ticket → Assign → Investigate → Resolve → Customer Confirm → Close.
    """,
    'category': 'Services/Helpdesk',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'dcg_master_data',
        'dcg_project_delivery',
        'dcg_contract_management',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ticket_stage_data.xml',
        'views/warranty_team_views.xml',
        'views/warranty_sla_views.xml',
        'views/warranty_ticket_stage_views.xml',
        'views/warranty_ticket_tag_views.xml',
        'views/warranty_solution_views.xml',
        'views/warranty_activity_views.xml',
        'views/warranty_ticket_views.xml',
        'views/menu.xml',
        'views/contract_views.xml',
        'views/project_delivery_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
