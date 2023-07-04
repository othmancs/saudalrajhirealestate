# -*- coding: utf-8 -*-
{
    "name": "Journal Restriction User",
    "summary": """ Journal restriction by user  """,
    "description": """ Add a record rule on account journal based on allowed user on specific journal \
        to activate this feature please add the user to 'Journal Restriction' group""",
    "author": "Plustech",
    "website": "",
    "category": "Account",
    "version": "0.1",
    "depends": ["base", "account"],
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/account_journal.xml',
    ],
}
