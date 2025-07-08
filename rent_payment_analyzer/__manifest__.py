{
    'name': 'محلل جدول دفعات التأجير',
    'version': '15.0.1.1.0',
    'summary': 'تحليل مرفقات PDF لاستخراج جدول الدفعات',
    'description': """
        يقوم هذا الموديول بتحليل ملفات PDF المرفقة بطلبات التأجير
        لاستخراج جدول الدفعات وحساب عدد الدفعات المتبقية.
    """,
    'author': 'Othmancs',
    'website': 'https://tbarholding.com',
    'category': 'Sales/Rental',
    'depends': ['sale', 'sale_renting'],
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
