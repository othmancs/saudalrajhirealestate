# -*- coding: utf-8 -*-

{
    'name': 'Print Journal Entries Report in Odoo',
    'version': '18.0.1.0.0',
    'category': 'Account',
    'summary': 'Allow to print pdf report of Journal Entries.',
    'description': """
    Allow to print pdf report of Journal Entries.
    journal entry
    print journal entry 
    journal entries
    print journal entry reports
    account journal entry reports
    journal reports
    account entry reports""",
    'depends': ['base', 'account'],
    'data': [
            'report/report_journal_entries.xml',
            'report/report_journal_entries_view.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            '/print_journal_entries/static/src/css/style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}
