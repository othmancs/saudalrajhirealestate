from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    maintenance_request_id = fields.Many2one('maintenance.request')
    pay_with_custody = fields.Boolean('Pay With Custody')
    custody_journal_id = fields.Many2one('account.journal', string='Journal')

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        balance = self.env['account.move.line'].sudo().search(
            [('account_id', '=', self.custody_journal_id.default_account_id.id), ('journal_id', '=', self.custody_journal_id.id)]).mapped('balance')
        if len(balance) > 0 and balance[0] < self.amount_total:
            raise UserError("Cash journal balance is not available.")
        return {
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
