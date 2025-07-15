{
    "name": "Accounting with Operating Units",
    "summary": "Introduces Operating Unit (OU) in invoices and "
    "Accounting Entries with clearing account",
    "version": "18.0.1.0.0",  # Updated for Odoo 18
    "author": "ForgeFlow, "
    "Serpent Consulting Services Pvt. Ltd.,"
    "WilldooIT Pty Ltd,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/operating-unit",
    "category": "Accounting & Finance",
    "depends": ["account"],  # Removed analytic_operating_unit dependency
    "license": "LGPL-3",
    "data": [
        # "security/account_security.xml",
        "views/account_move_view.xml",
        "views/account_journal_view.xml",
        "views/company_view.xml",
        "views/account_payment_view.xml",
        "views/account_invoice_report_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
