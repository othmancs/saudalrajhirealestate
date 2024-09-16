# -*- coding: utf-8 -*-
{
    'name': "Customer Tickets",

    'summary': """
        Customer Tickets""",

    'description': """
This module allow customer has a valid subscription to submit ticket for support team. 
First you neet to activate developer mode in order to set up configuration so go to menu:
Tickets -> Configuration -> Subscription create new record with db,user,password the press get date data button, it will 
get subscription code and subscription status, 
You can submit a ticket while the status of subscription is running
 """,

    'author': "PlusTech",
    'website': "http://www.plustech-it.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/cron_data.xml',
        'data/database_info_data.xml',
        'data/mail_activity.xml',
        'views/customer_ticket.xml',
        'views/subscription.xml',
        'views/ticket_type.xml',
        'views/package_ticket_type.xml',
        'views/feedback.xml',
        'views/ir_attachment.xml',
    ],
        'assets': {
        'web.assets_backend': [
            '/customer_tickets/static/src/scss/sale.scss',
            '/customer_tickets/static/src/js/sale_dashboard.js',
        ],
        'web.assets_qweb': [
            'customer_tickets/static/src/xml/**/*',
        ],
    },
    'application': True,
    'license': 'LGPL-3',
}
