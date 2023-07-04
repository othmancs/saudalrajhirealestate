from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('review', 'Reviewed'),
                                            ('posted',)],  ondelete={'review': 'set default'})

    def action_review(self):
        self.sudo().write({'state': 'review'})

