# -*- coding: utf-8 -*-
{
    'name': 'Pivot View Extention',
    'summary': 'Extention the functionality for the pivot groupby',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    'description': """
            Customized Odoo Web core module, to extend the functionality for 
            pivot groupby.
    """,
    "assets": {
        "web.assets_backend": [
            'pivot_view_extention/static/src/views/pivot/custom_pivot_model.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
