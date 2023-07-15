from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    maintenance_request_id = fields.Many2one('maintenance.request')
    pay_with_custody = fields.Boolean('Pay With Custody')
    maintenance_exp_invoice = fields.Boolean('Expense Invoice')
    maintenance_cus_invoice = fields.Boolean('Customer Invoice')
    pay_with_custody = fields.Boolean('Pay With Custody')
    custody_journal_id = fields.Many2one('account.journal', string='Journal')

    def action_view_maint_request(self):
        return{
            'name': _('Maintenance'),
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain':[('id','=',self.maintenance_request_id.id)],
            # 'target': 'new',
            'type': 'ir.actions.act_window',

        }


    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        balance = self.maintenance_request_id.journal_id.default_account_id.current_balance
        action = {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        print("################## self.pay_with_custody",self.pay_with_custody)
        print("################## self.custody_journal_id",self.custody_journal_id)
        if balance < self.amount_total and self.maintenance_request_id.pay_with_custody:
            raise UserError("Cash journal balance is not available.")
        if self.maintenance_request_id.pay_with_custody and self.maintenance_request_id.journal_id :
            action['context'].update({'default_journal_id': self.maintenance_request_id.journal_id.id})

        return action
