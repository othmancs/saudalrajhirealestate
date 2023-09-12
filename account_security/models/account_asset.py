from odoo import fields, models, api,_
from odoo.exceptions import UserError 


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    state = fields.Selection(selection_add=[('review', 'To Confirm'),
                                            ('open',)])

    def action_review(self):
        self.sudo().write({'state': 'review'})

    
    @api.model
    def create(self, vals):
        ret = super(AccountAsset, self).create(vals)
        if not self.user_has_groups('account_security.group_account_asset_create') and ret.asset_type =='purchase':
            raise UserError(_("You are not allowed to create"))
        if not self.user_has_groups('account_security.group_account_deferred_revenue_create') and ret.asset_type =='sale':
            raise UserError(_("You are not allowed to create"))
        if not self.user_has_groups('account_security.group_account_deferred_expense_create') and ret.asset_type =='expense':
            raise UserError(_("You are not allowed to create"))
        return ret

