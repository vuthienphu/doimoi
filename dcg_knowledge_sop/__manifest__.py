# -*- coding: utf-8 -*-
{
    'name': 'DCG Knowledge SOP',
    'version': '18.0.1.0.0',
    'summary': 'Knowledge base, SOP, FAQ, best practices, coding standards',
    'description': """
DCG Knowledge SOP — Kho Tri thức & Quy trình
==============================================

Quản lý tri thức dùng chung toàn công ty:

* SOP triển khai (Standard Operating Procedure)
* FAQ — câu hỏi thường gặp
* Best Practice — kinh nghiệm tốt
* Known Issue — lỗi đã biết + cách xử lý
* Coding Standard — quy chuẩn lập trình
* Guide — hướng dẫn nghiệp vụ

Tính năng:
* Article lifecycle: Draft → Review → Published → Archived
* Revision history (version control nội dung)
* Feedback / rating từ team
* Liên kết project, ticket, module
* View count tracking
* Kanban + tree + full-text search
    """,
    'category': 'Knowledge',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'dcg_master_data',
        'dcg_project_delivery',
        'dcg_helpdesk_warranty',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/category_data.xml',
        'views/knowledge_category_views.xml',
        'views/knowledge_tag_views.xml',
        'views/knowledge_article_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
