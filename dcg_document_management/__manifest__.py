# -*- coding: utf-8 -*-
{
    'name': 'DCG Document Management',
    'version': '18.0.1.0.0',
    'summary': 'DMS: folder, version, review, template, checklist, business links',
    'description': """
DCG Document Management — DMS cho vòng đời dự án
====================================================

Trung tâm tài liệu toàn hệ thống, thay thế ir.attachment đơn thuần:

* Folder tree (parent/child)
* Document type (quy định approval, version, portal, retention)
* Category & tag đa chiều
* Version control: document → version → ir.attachment
* Review / approval workflow
* Template cho tạo nhanh (NDA, Proposal, BRD...)
* Business link: 1 document liên kết nhiều object (project, contract, ticket, trip)
* Checklist: đảm bảo đủ tài liệu trước Go-live

Lifecycle: Draft → Review → Approved → Published → Archived.
    """,
    'category': 'Document Management',
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
        'views/document_folder_views.xml',
        'views/document_category_views.xml',
        'views/document_type_views.xml',
        'views/document_tag_views.xml',
        'views/document_template_views.xml',
        'views/document_version_views.xml',
        'views/document_review_views.xml',
        'views/document_checklist_views.xml',
        'views/document_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
