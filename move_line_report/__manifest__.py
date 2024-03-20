# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Move Line Report',
    'version': '15.0.2.0.0',
    'category': ' ',
    'summary': '',
    'sequence': '10',
    'author': 'Plus Tech',
    'license': 'LGPL-3',
    'company': 'Plus Tech',
    'maintainer': 'Plus Tech',
    'support': 'info@plustech-it.com',
    'website': 'www.plustech-it.com',
    'depends': ["base", "account","renting"],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizards/move_line_report_wizard_view.xml',
    ],
    'images': ['static/description/banner.gif'],
}
