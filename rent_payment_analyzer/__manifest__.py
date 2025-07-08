{
    'name': 'Rent Payment Schedule Analyzer',
    'version': '15.0.1.0.3',
    'summary': 'Analyze PDF attachments in Rental Orders to extract Rent Payments Schedule',
    'description': """
        This module analyzes PDF attachments in rental orders to extract 
        Rent Payments Schedule and calculate number of payments.
        Uses PyMuPDF for reliable PDF processing.
    """,
    'author': 'Othmancs',
    'website': 'https://tbarholding.com',
    'category': 'Sales/Sales',
    'depends': ['sale_renting'],
    'external_dependencies': {
        'python': ['fitz', 'pymupdf'],
    },
    'data': [
        'views/rental_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rent_payment_analyzer/static/src/js/pdf_analyzer.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}