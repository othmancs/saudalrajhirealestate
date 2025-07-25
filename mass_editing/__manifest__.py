# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mass Editing',
    'version': '14.0.1.1.1',
    'author': 'Serpent Consulting Services Pvt. Ltd., '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'category': 'Tools',
    'website': 'https://github.com/OCA/server-ux',
    'license': 'AGPL-3',
    'summary': 'Mass Editing',
    'uninstall_hook': 'uninstall_hook',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
    ],
}
