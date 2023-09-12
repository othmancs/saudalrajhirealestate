from odoo import fields, models, api,_
from odoo.exceptions import UserError 


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('review', 'Reviewed'),
                                            ('posted',)],  ondelete={'review': 'set default'})

    def action_review(self):
        self.sudo().write({'state': 'review'})

    @api.model
    def create(self, vals):
        ret = super(AccountMove, self).create(vals)
        if not self.user_has_groups('account_security.group_account_customer_invoices_create') and ret.move_type =='out_invoice':
            raise UserError(_("You are not allowed to create"))
        if not self.user_has_groups('account_security.group_account_vendor_bill_create') and ret.move_type =='in_invoice':
            raise UserError(_("You are not allowed to create"))
        if not self.user_has_groups('account_security.group_account_journal_entry_create') and ret.move_type =='entry':
            raise UserError(_("You are not allowed to create"))
        return ret


    
    def action_post(self):
        ret = super(AccountMove, self).action_post()
        if not self.user_has_groups('account_security.group_account_customer_invoices_confirm') and self.move_type =='out_invoice':
            raise UserError(_("You are not allowed to confirm"))
        if not self.user_has_groups('account_security.group_account_vendor_bill_confirm') and self.move_type =='in_invoice':
            raise UserError(_("You are not allowed to confirm"))
        if not self.user_has_groups('account_security.group_account_journal_entry_confirm') and self.move_type =='entry':
            raise UserError(_("You are not allowed to confirm"))
        return ret


    