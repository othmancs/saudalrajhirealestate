# -*- coding: utf-8 -*-
{
    'name': "Accounting Advanced ",
    'summary': """  Accounting Advanced""",
    'description': """  Accounting Asset  """,
    'author': "Plus Tech",
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'depends': ['account', 'account_asset', 'renting'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/asset.xml',
        'views/account_move.xml',
        'views/sale_rental.xml',
    ],
}
