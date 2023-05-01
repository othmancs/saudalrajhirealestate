# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_analytic_group = None

    @api.model
    def _init_analytic_group(self, options, previous_options=None):
        if not self.filter_analytic_group:
            return options
        options['analytic_group'] = True
        options['analytic_group_ids'] = previous_options and previous_options.get('analytic_group_ids') or []
        selected_analytic_group_ids = [int(partner) for partner in options['analytic_group_ids']]
        selected_analytic_group = selected_analytic_group_ids and self.env['account.analytic.group'].browse(selected_analytic_group_ids) or self.env['account.analytic.group']
        options['selected_analytic_group_ids'] = selected_analytic_group.mapped('name')
        # if options['selected_analytic_group_ids']:
        #     options[]
        return options
    
    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountReport, self)._get_options(previous_options)
        self._init_analytic_group(options, previous_options)
        return options

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('analytic_group_ids'):
            analytic_group_ids = self.env['account.analytic.group'].browse([int(branch) for branch in options.get('analytic_group_ids', [])])
            ctx['analytic_group_ids'] = analytic_group_ids.ids
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        info = super(AccountReport, self).get_report_informations(options)
        if options and options.get('analytic_group'):
            options['selected_analytic_group_ids'] = [self.env['account.analytic.group'].browse(int(branch)).name for branch in options.get('analytic_group_ids', [])]
        return info
