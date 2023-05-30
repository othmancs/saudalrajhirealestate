# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.tools.misc import format_date


class report_account_general_ledger(models.AbstractModel):
    _inherit = "account.general.ledger"

    filter_analytic_group = True
    filter_operation = True

    @api.model
    def _get_options_domain(self, options):
        domain = super(report_account_general_ledger, self)._get_options_domain(options)

        if options.get('analytic_group') and options.get('analytic_group_ids'):
            print("aaaaaaaaa")
            domain += [('analytic_group', 'in', options.get('analytic_group_ids'))]

        if options.get('operating_unit_id') and options.get('operating_unit_ids'):
            domain += [('operating_unit_id', 'in', options.get('operating_unit_ids'))]


        return domain

