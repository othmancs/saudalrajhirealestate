from odoo import fields, models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    state = fields.Selection(selection_add=[('review', 'To Confirm'),
                                            ('open',)])

    def action_review(self):
        self.sudo().write({'state': 'review'})

