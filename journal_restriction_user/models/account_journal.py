from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    allowed_user_ids = fields.Many2many(comodel_name='res.users', string='Allowed Users')

