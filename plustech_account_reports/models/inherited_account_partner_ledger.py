# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools.misc import format_date


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger'

    filter_analytic_group = True

    # @api.model
    # def _get_options_domain(self, options):
    #     domain = super(AccountPartnerLedger, self)._get_options_domain(options)

    #     if options.get('analytic_group') and options.get('analytic_group_ids'):
    #         domain += [('analytic_group', 'in', options.get('analytic_group_ids'))]

    #     return domain
   