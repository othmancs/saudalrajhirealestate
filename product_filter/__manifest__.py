{
    'name': 'Product Unit State Filter',
    'version': '15.0.1.0.0',
    'summary': 'Filter products in sale order based on unit state',
    'description': """
        This module filters products in sale order lines based on the unit_state field.
        Only products with empty unit_state will be shown in selection.
    """,
    'author': 'Othmancs',
    'website': 'https://www.Tbarholding.com',
    'category': 'Sales/Sales',
    'depends': ['sale', 'product'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}