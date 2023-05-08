{
    'name': 'Property Maintenance',
    'version': '15.0.0.0.3',
    'author': 'Maintenance Requests Management',
    'category': 'Generic/Real Estate',
    'website': "www.plustech-it.com",
    'summary': """""",
    'description': """""",
    'depends': ['base', 'product', 'sale', 'hr', 'rating','stock','stock_request', 'operating_unit', 'rent_customize'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/maintenance_request_data.xml',
        'views/maintenance_request_views.xml',
        'views/maintenance_issue_type_views.xml',
        'views/res_config_settings_views.xml',
        'templates/maintenance_request_portal_templates.xml',
        'wizards/wiz_maintenance_request_refuse_views.xml',
        'wizards/wiz_maintenance_request_assign_views.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            "/real_estate_maintenance/static/src/js/maintenance_request.js"
        ],
    },
    'sequence': 21,
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
