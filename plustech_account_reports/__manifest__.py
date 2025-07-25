{
    'name': 'Plustech Account Reports',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'depends': [ 'account', 'account_reports', 'account_accountant', 'operating_unit'],
    'data': [
        # 'security/security.xml',
        # 'views/branch_branch_views.xml',
        'views/account_move_views.xml',
        # 'views/account_report_view.xml',
        'views/search_template_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'plustech_account_reports/static/src/js/account_report_analytic_group.js',
            'plustech_account_reports/static/src/js/account_reports_operating_unit.js',

        ],
    },
    'installable': True,
    'application': True,
}
