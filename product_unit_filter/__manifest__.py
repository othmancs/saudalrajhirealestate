{
    'name': 'Product Unit Filter in Sales',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Filter products in sale order based on unit_state',
    'depends': ['sale', 'product'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
