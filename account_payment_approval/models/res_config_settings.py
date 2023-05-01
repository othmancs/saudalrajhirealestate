# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _domain_company(self):
        company = self.env.company
        return ['|', ('company_id', '=', False), ('company_id', '=', company.id)]

    approval_inbound_journals = fields.Many2many('account.journal',  'inbound_journals',
                                                 string="Inbound Journal", domain=_domain_company)
    approval_outbound_journals = fields.Many2many('account.journal',  'outbound_journals',
                                                  string="Outbound Journal", domain=_domain_company)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_journal_ids(self):
        company = self.env.company
        return [('id', 'in', self.env['account.journal'].search([('type', 'in', ['cash', 'bank'])]).ids),
                '|', ('company_id', '=', False), ('company_id', '=', company.id)]

    payment_approval = fields.Boolean(
        'Payment Approval', config_parameter='account_payment_approval.payment_approval')
   
    approval_amount = fields.Float('Minimum Approval Amount',
                                   config_parameter='account_payment_approval.approval_amount',
                                   help="If amount is 0.00, All the payments go through approval.")
    approval_currency_id = fields.Many2one('res.currency', string='Approval Currency',
                                           config_parameter='account_payment_approval.approval_currency_id',
                                           help="Converts the payment amount to this currency if chosen.")

    approval_inbound = fields.Boolean(
        'Inbound Approval', config_parameter='account_payment_approval.approval_inbound')
    approval_inbound_journals = fields.Many2many('account.journal', 'inbound_journals_rel', 'x_id', 'journal_id',
                                                 string="Inbound Journal",
                                                 default=lambda self: self.env.user.company_id.approval_inbound_journals.ids,
                                                 domain=_get_journal_ids)

    approval_outbound = fields.Boolean(
        'Outbound Approval', config_parameter='account_payment_approval.approval_outbound')
    approval_outbound_journals = fields.Many2many('account.journal', 'outbound_journals_rel', 'x_id', 'journal_id',
                                                 string="Inbound Journal",
                                                 default=lambda self: self.env.user.company_id.approval_outbound_journals.ids,
                                                 domain=_get_journal_ids)


    @api.model
    def create(self, vals):
        res = super(ResConfigSettings, self).create(vals)
        res.company_id.write({'approval_inbound_journals': vals['approval_inbound_journals'], 'approval_outbound_journals': vals['approval_outbound_journals']})

        return res
