# -*- coding: utf-8 -*-


{
    "name": "Purchase Request",
    "summary": "Internal request for stock",
    "version": "15.0.2.0",
    "license": "LGPL-3",
    "website": "www.plustech.com",
    "author": "Plus Tech",
    "category": "Warehouse Management",
    "depends": ["stock", "hr"],
    "data": [
        "security/stock_request_security.xml",
        "security/ir.model.access.csv",
        'views/stock_request_reports.xml',
        "views/stock_request_views.xml",
        'views/res_config_settings_views.xml',
        "views/stock_request_menu.xml",
        "data/stock_request_sequence_data.xml",
        'wizard/pending_orders_wizard_view.xml',
        'wizard/product_quantity.xml',
        'wizard/purchase_wizard.xml',
    ],
    "installable": True,
}
