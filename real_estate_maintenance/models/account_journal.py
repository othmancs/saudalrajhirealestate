from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_custody = fields.Boolean('Is Custody')


