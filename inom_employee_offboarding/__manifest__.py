# -*- coding: utf-8 -*-
{
    'name': 'Bravestars Offboarding',
    'version': '19.0.1.0.0',
    'category': 'Bravestars',
    'summary': 'Manage employee offboarding with a multi-level resignation '
               'and relieving approval workflow.',
    'description': """
Employee Offboarding Management
===============================
Provides a structured offboarding process for employees leaving the company.

Key capabilities:
    * Employees raise an offboarding request and submit it to their manager.
    * Multi-level approval: reporting manager, then HR.
    * Notice period and relieving date are set during the process.
    * Configurable offboarding reasons.
    * Configurable clearance checklist with progress tracking.
    * Rejection captures a documented reason.
    * Printable offboarding request as a PDF report.
    * Dedicated security roles for coordinators and HR.
    * On relieving, the employee record is archived automatically.
    """,
    'license': 'OPL-1',
    'depends': [
        'base',
        'mail',
        'hr',
        'survey',
        'hr_level',
        'hr_to_offboarding',
        'hr_custom',
    ],
    'data': [
        'security/offboarding_security.xml',
        'security/ir.model.access.csv',

        'data/offboarding_sequence.xml',
        'data/ir_parameter.xml',
        'data/offboarding_survey_data.xml',
        'data/mail_template_data.xml',
        'data/offboarding_cron.xml',

        'wizard/offboarding_reject_wizard_views.xml',

        'views/offboarding_reason_views.xml',
        'views/offboarding_checklist_views.xml',
        'views/offboarding_payment_views.xml',
        'views/offboarding_request_views.xml',
        'views/offboarding_dashboard.xml',
        'views/offboarding_mail_template_views.xml',
        'views/offboarding_menus.xml',
        'views/survey_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'inom_employee_offboarding/static/src/scss/offboarding.css',
            'inom_employee_offboarding/static/src/dashboard/offboarding_dashboard.js',
            'inom_employee_offboarding/static/src/dashboard/offboarding_dashboard.xml',
            'inom_employee_offboarding/static/src/dashboard/offboarding_dashboard.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
