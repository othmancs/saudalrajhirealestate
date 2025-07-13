# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################

{
    'name': 'ZKTeco biometric attendance',
    'version': '18.0.1.0.0',
    'author': 'Bashier Elbashier',
    'category': 'Human Resources',
    'summary': 'Manage employee attendances performed by ZKTeco devices',
    'depends': ['hr', 'hr_attendance_multi_company', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/zk_machine_att_log_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
