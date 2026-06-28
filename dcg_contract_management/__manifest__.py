# -*- coding: utf-8 -*-
{
    'name': 'DCG Contract Management',
    'version': '18.0.1.0.0',
    'summary': 'End-to-end contract lifecycle: line, payment schedule, appendix, acceptance',
    'description': """
DCG Contract Management
========================

Quản lý toàn bộ vòng đời hợp đồng dịch vụ/dự án sau giai đoạn presales.

6 model chính:
* dcg.contract — header hợp đồng, inherit dcg.approval.mixin (contract_approval)
* dcg.contract.line — hạng mục / scope
* dcg.contract.payment — lịch thanh toán (%, cố định)
* dcg.contract.appendix — phụ lục, inherit dcg.approval.mixin (appendix_approval)
* dcg.contract.appendix.line — chi tiết thay đổi phụ lục
* dcg.contract.acceptance — biên bản nghiệm thu

Tích hợp:
* Tạo contract từ sale.order (quotation) hoặc crm.lead
* Map estimate line → contract line
* Approval hợp đồng & phụ lục qua dcg_approval_matrix
* Phụ lục effective → cập nhật contract amount/end_date/scope

Flow: Quotation/Lead → Contract → Approval → Active → Appendix/Acceptance/Payment → Done → Closed.
    """,
    'category': 'Sales',
    'author': 'Công ty TNHH Đổi Mới G.R.O.U.P',
    'website': 'https://doimoigroup.vn',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'crm',
        'mail',
        'dcg_master_data',
        'dcg_approval_matrix',
        'dcg_crm_presales',
    ],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',

        # data
        'data/ir_sequence_data.xml',

        # wizard
        'wizard/contract_close_wizard_views.xml',

        # views — actions before menu, extensions last
        'views/contract_line_views.xml',
        'views/contract_payment_views.xml',
        'views/contract_acceptance_views.xml',
        'views/contract_appendix_views.xml',
        'views/contract_views.xml',
        'views/menu.xml',
        'views/sale_order_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
