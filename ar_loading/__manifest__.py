# -*- coding: utf-8 -*-
{
    'name': "Cat Loading",
    'summary': "Upgrade your loading display to make the user experience more enjoyable with a cat-themed loading screen.",
    'description': """
    This module enhances the loading experience in Odoo by replacing the standard loading indicator with a playful cat-themed animation. It aims to make waiting times more enjoyable for users, adding a touch of fun to the interface.
    """,
    'author': "ARscript",
    'category': 'Productivity',
    'version': '18.0.1.0.0',
    'price': 0.0,
    'currency': 'USD',
    'images': ['static/description/cover.png'],
    'depends': ['web'],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'ar_loading/static/src/webclient/loading_indicator/loading_indicator.js',
            'ar_loading/static/src/webclient/loading_indicator/loading_indicator_cat1.scss',
            'ar_loading/static/src/webclient/loading_indicator/loading_indicator_cat2.scss',
            'ar_loading/static/src/xml/loading_indicator.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
