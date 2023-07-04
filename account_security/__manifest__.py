
{
    'name': 'Accounting Security',
    'version': '15.0.0.0',
    'category': 'Accounting/Accounting/Assets',
    'summary': 'accounting security',
    "description": """
            accounting security
       """,
    'author': 'Plus Technology Co',
    'website': 'www.plustech-it.com',
    'depends': ['account', 'account_asset'],
    'data': [
        'security/account_asset_security.xml',
        'security/account_account_security.xml',
        'security/account_budget_security.xml',
        'security/ir.model.access.csv',
        'views/account_asset.xml',
        'views/account_account.xml',
        'views/account_budget_view.xml',
        'views/account_payment.xml',
        'views/account_reports.xml',
    ],
    'qweb': [],
    'web.assets_backend': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

