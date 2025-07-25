# -*- coding: utf-8 -*-
{
    'name': "Rent Customize",
    'summary': """Sale Renting Customization""",
    'category': 'Sales Management',
    'version': '0.1',
    'depends': ['sale', 'sale_renting', 'renting', 'web_google_maps', 'invoice_templates'],
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
        'report/reports_layout_template.xml',
        'views/res_setting.xml',
        'views/eviction_report.xml',
        'views/renting_views.xml',
        'data/data.xml',
        'data/sequence_data.xml',
        'report/report_pickup_template.xml',
        'report/report_return_template.xml',
        'report/vacating_property_template.xml',
        'report/transfer_template.xml',
        'report/commercial_template.xml',
        'report/personal_template.xml',
        'report/value_update_template.xml',
        'report/contract_termination.xml',
        'report/payment_claim_template.xml',
        'report/contract_reminder_report_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            '/rent_customize/static/description/src/css/style.css',
        ],
    },
}
