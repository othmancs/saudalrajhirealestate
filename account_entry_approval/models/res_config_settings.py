# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _domain_company(self):
        company = self.env.company
        return ['|', ('company_id', '=', False), ('company_id', '=', company.id)]

    need_approval_journals = fields.Many2many('account.journal', 'journal_entry_rel', string="Approval Journal",
                                              domain=_domain_company,)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'



    def _get_journal_ids(self):
        return [('id', 'in', self.env['account.journal'].search([('type', 'in', ['cash', 'bank'])]).ids)]

    entry_approval = fields.Boolean(
        'Journal Entry Approval', config_parameter='account_entry_approval.entry_approval')
   
    need_approval_journals = fields.Many2many('account.journal', 'journal_entry_rel',
                                                 string="Approval Journal",related='company_id.need_approval_journals',readonly=False,
                                             )

