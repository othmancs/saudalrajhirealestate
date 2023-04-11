# -*- coding: utf-8 -*-
{
    'name': "Rent Customization",
    "version": "15.0.0.6",
    'summary': """
       Operational Addons""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ibrahim Abdullatif",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_renting', 'sale_operating_unit', 'analytic', 'account_asset', 'l10n_gcc_invoice',
                'product'],

    # always loaded
    'data': [
        'views/vw_menu_items.xml',
        # 'views/assets.xml',
        'views/vw_rent_account_move_inherit.xml',
        'views/vw_rent_config_property_types.xml',
        'views/vw_rent_config_property_purposes.xml',
        'views/vw_rent_config_property_maintenance_types.xml',
        'views/vw_rent_config_property_maintenance_statuses.xml',
        'views/vw_rent_config_unit_finishes.xml',
        'views/vw_rent_config_unit_maintenance_types.xml',
        'views/vw_rent_config_unit_maintenance_statuses.xml',
        'views/vw_rent_config_unit_overlooks.xml',
        'views/vw_rent_config_unit_types.xml',
        'views/vw_rent_maintenance_pivot_report.xml',
        'views/vw_rent_config_unit_purposes.xml',
        'views/vw_rent_res_partner_inherit.xml',
        'views/vw_rent_product_inherit.xml',
        'views/vw_rent_product.xml',
        'views/vw_rent_property.xml',
        'views/vw_rent_property_elevator.xml',
        'views/vw_rent_property_maintenance.xml',
        'views/vw_rent_unit_maintenance.xml',
        'views/vw_rent_sale_order_inherit.xml',
        'views/vw_rent_sale_order_lines.xml',
        'views/vw_product_configuration.xml',
        'report/report_pickup.xml',
        'report/report_return.xml',
        'report/report_property_ eviction.xml',
        'data/demo_products.xml',
        'security/renting_security.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    "installable": True,
    "auto_install": False,
}
