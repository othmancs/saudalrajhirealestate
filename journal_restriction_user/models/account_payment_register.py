from odoo import models, _, api, fields
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    

    def get_domain(self):
        if self.user_has_groups('journal_restriction_user.group_user_journal_restrict'):
            journal_ids = self.env['account.journal'].search([('allowed_user_ids', 'in', self.env.user.id)])
            return [('id','in',journal_ids.ids),('type', 'in', ('bank', 'cash'))]
        else :
            journal_ids = self.env['account.journal'].search([])
            return [('id','in',journal_ids.ids),('type', 'in', ('bank', 'cash'))]

    # journal_id = fields.Many2one(comodel_name='account.journal', string='Journal',domain=get_domain)
    allowed_journal_id = fields.Many2many(comodel_name='account.journal', string='Journal',compute="get_domain_ids")
   
    
    @api.onchange('partner_id')
    def get_domain_ids(self):
        for rec in self :
            if self.user_has_groups('journal_restriction_user.group_user_journal_restrict'):
                journal_ids = self.env['account.journal'].search([('allowed_user_ids', 'in', self.env.user.id),('type', 'in', ('bank', 'cash'))])
                rec.allowed_journal_id = journal_ids
            else :
                journal_ids = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
                rec.allowed_journal_id = journal_ids


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def get_domain(self):
        if self.user_has_groups('journal_restriction_user.group_user_journal_restrict'):
            journal_ids = self.env['account.journal'].search([('allowed_user_ids', 'in', self.env.user.id)])
            return [('id','in',journal_ids.ids),('type', 'in', ('bank', 'cash'))]
        else :
            journal_ids = self.env['account.journal'].search([])
            return [('id','in',journal_ids.ids),('type', 'in', ('bank', 'cash'))]


    journal_id = fields.Many2one(comodel_name='account.journal', string='Journal',domain=get_domain)
    
