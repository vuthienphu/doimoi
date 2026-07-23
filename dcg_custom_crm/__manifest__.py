# -*- coding: utf-8 -*-
{
    'name': 'DCG Custom CRM',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Custom CRM extensions for DCG',
    'description': """
        Custom CRM module for DCG-specific lead, opportunity, and sales workflows.
    """,
    'author': 'DM Group',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'project',
        'mail',
        'contacts',
        'dcg_crm_cost',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/crm_team_commission_wizard_views.xml',
        'wizard/crm_survey_wizard_views.xml',
        'views/crm_team_views.xml',
        'views/crm_lead_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
