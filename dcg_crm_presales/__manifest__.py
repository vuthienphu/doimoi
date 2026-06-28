# -*- coding: utf-8 -*-
{
    'name': 'DCG CRM Presales',
    'version': '18.0.1.0.0',
    'summary': 'Presales workflow: requirement survey, solution scope, estimate, presales cost, deal approval',
    'description': """
DCG CRM Presales
==================

Mở rộng CRM/Sales để quản lý toàn bộ giai đoạn trước hợp đồng:

* Mở rộng res.partner: phân loại khách hàng, account manager, ngành/nguồn
* Mở rộng crm.lead: business discovery, estimate summary, commercial status, deal approval
* Requirement Survey (dcg.crm.requirement) — biên bản khảo sát
* Solution Scope (dcg.crm.solution.scope) — hạng mục giải pháp đề xuất
* Estimate + Estimate Line (dcg.crm.estimate / dcg.crm.estimate.line) — effort/cost/revenue theo version
* Presales Cost (dcg.crm.presales.cost) — chi phí trước bán hàng
* Deal approval qua dcg_approval_matrix (approval_type = deal_approval)
* Tạo quotation (sale.order) từ lead/estimate

Flow: Lead -> Requirement -> Scope -> Estimate -> Approval -> Quotation -> (dcg_contract_management).
    """,
    'category': 'Sales/CRM',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'sale',
        'contacts',
        'mail',
        'dcg_master_data',
        'dcg_approval_matrix',
    ],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',

        # data
        'data/ir_sequence_data.xml',

        # views (actions must load before menu.xml references them)
        'views/res_partner_views.xml',
        'views/crm_requirement_views.xml',
        'views/crm_solution_scope_views.xml',
        'views/crm_estimate_views.xml',
        'views/crm_presales_cost_views.xml',
        'views/menu.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
