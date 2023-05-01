# -*- coding: utf-8 -*-


{
    'name': 'Payment Approvals',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'author': 'PlusTech Team',
    'company': 'PlusTech Team',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_payment_view.xml',
        'views/account_journal.xml',
        'views/menu-item.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
