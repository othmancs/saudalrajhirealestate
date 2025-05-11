# -*- coding: utf-8 -*-


{
    "name": "Biostar 2 Biometric Attendance Integration",
    "version": "15.0",
    "category": "Human Resources",
    "sequence": 1,
    "author": "",
    "summary": "Biometric attendance integration",
    "website": "",
    "license": "Other proprietary",
    "description": """
 Synchronization of employee attendance with biometric machine ...""",
    "depends": ["hr_attendance", "resource"],
    "data": [
        "views/attendance_logs_views.xml",
        "security/ir.model.access.csv",
        #'views/mail_templates.xml',
        "data/ir_cron.xml",
        "views/biostar_api.xml",
        "wizard/attendance_report_wizard_view.xml",
        "views/menu.xml",
        "views/hr_views.xml",
    ],
    "demo": [],
    "images": ["images/biostar_2_icon.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
