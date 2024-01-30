# -*- coding: utf-8 -*-


{
    'name': 'Journal Entry Approvals',
    'version': '15.0.1.0.1',
    'category': 'Accounting',
    'author': 'PlusTech Team',
    'company': 'PlusTech',
    'depends': ['account'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/account_move_view.xml',
        'views/account_journal.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
