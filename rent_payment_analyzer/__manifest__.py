{
    'name': 'Rent Payment Schedule Analyzer',
    'version': '15.0.1.0.0',
    'summary': 'Analyze PDF attachments to extract Rent Payments Schedule',
    'description': """
        This module analyzes PDF attachments in invoices to extract 
        Rent Payments Schedule and calculate number of payments.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'data': [
        'views/invoice_view.xml',
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