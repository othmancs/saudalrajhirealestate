# -*- coding: utf-8 -*-
{
    'name': "Rent Customize",
    'summary': """Sale Renting Customization""",
    'category': 'Sales Management',
    'version': '0.1',
    'depends': ['sale_renting', 'renting', 'web_google_maps'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'cron/cron.xml',
        'wizard/transfer_apartment_wizard.xml',
        'views/product.xml',
        'views/sales_views.xml',
        'views/rent_property_build.xml',
        'views/sale_rental_schedule.xml',
        'views/attachment.xml',
        'views/move.xml',
        'views/rent_letter_template.xml',
        'report/contract.xml',
        'report/transfer.xml',
        'views/res_setting.xml',
        'data/data.xml',
    ]
}
