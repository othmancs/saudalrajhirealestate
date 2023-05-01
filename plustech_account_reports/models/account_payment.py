from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_default_branch(self):
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        res['domain']['journal_id'] = \
            self.payment_type == 'inbound' and [('at_least_one_inbound', '=', True)] or \
            [('at_least_one_outbound', '=', True)]
        res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash')))
        res['domain']['journal_id'].append(('id', 'in', self.env.user.bank_cash_journal_ids.ids))
        return self.env.user.branch_id

    partner_id = fields.Many2one('res.partner',
                                 string='Partner',
                                 tracking=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id)]")

    branch_id = fields.Many2one('branch.branch',
                                string='Branch',
                                store=True,
                                default=_get_default_branch,
                                domain=lambda self: [('id', 'in', self.env.user.allowed_branches.ids)],
                                readonly=False)

    def _compute_journal_domain_and_types(self):
        journal_type = ['bank', 'cash']
        domain = []
        if self.invoice_ids:
            domain.append(('company_id', '=', self.invoice_ids[0].company_id.id))
        if self.currency_id.is_zero(self.amount) and self.has_invoices:
            # In case of payment with 0 amount, allow to select a journal of type 'general' like
            # 'Miscellaneous Operations' and set this journal by default.
            journal_type = ['general']
            self.payment_difference_handling = 'reconcile'
        else:
            if self.payment_type == 'inbound':
                domain.append(('at_least_one_inbound', '=', True))
                domain.append(('id', 'in', self.env.user.bank_cash_journal_ids.ids))
            else:
                domain.append(('at_least_one_inbound', '=', True))
                domain.append(('id', 'in', self.env.user.bank_cash_journal_ids.ids))
        return {'domain': domain, 'journal_types': set(journal_type)}
