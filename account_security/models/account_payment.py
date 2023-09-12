from odoo import fields, models, api,_
from odoo.exceptions import UserError 



class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # state = fields.Selection(selection_add=[('review', 'Reviewed'),
    #                                         ('posted',)],  ondelete={'review': 'set default'})

    def action_review(self):
        self.sudo().write({'state': 'review'})

    @api.model
    def create(self, vals):
        ret = super(AccountPayment, self).create(vals)
        if not self.user_has_groups('account_security.group_account_customer_payment_create') and ret.payment_type == 'inbound':
            raise UserError(_("You are not allowed to create"))
        if not self.user_has_groups('account_security.module_category_accounting_accounting_vendor_payment') and ret.payment_type == 'outbound':
            raise UserError(_("You are not allowed to create"))
        return ret
