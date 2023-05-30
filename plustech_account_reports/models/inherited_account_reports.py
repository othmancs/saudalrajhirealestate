# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_analytic_group = None
    filter_operation = None

    @api.model
    def _init_analytic_group(self, options, previous_options=None):
        if not self.filter_analytic_group:
            return options
        options['analytic_group'] = True
        options['analytic_group_ids'] = previous_options and previous_options.get('analytic_group_ids') or []
        selected_analytic_group_ids = [int(partner) for partner in options['analytic_group_ids']]
        selected_analytic_group = selected_analytic_group_ids and self.env['account.analytic.group'].browse(selected_analytic_group_ids) or self.env['account.analytic.group']
        options['selected_analytic_group_ids'] = selected_analytic_group.mapped('name')
        return options
    
    @api.model
    def _init_operation(self, options, previous_options=None):
        if not self.filter_operation:
            return options
        options['operating_unit_id'] = True
        options['operating_unit_ids'] = previous_options and previous_options.get('operating_unit_ids') or []
        selected_operating_unit_ids = [int(partner) for partner in options['operating_unit_ids']]
        selected_operating_unit = selected_operating_unit_ids and self.env['operating.unit'].browse(selected_operating_unit_ids) or self.env['operating.unit']
        options['selected_operating_unit_ids'] = selected_operating_unit.mapped('name')

        return options
    
    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountReport, self)._get_options(previous_options)
        self._init_analytic_group(options, previous_options)
        self._init_operation(options, previous_options)

        return options
    
    # @api.model
    # def _get_options_analytic_domain(self, options):
    #     domain = []
    #     if options.get('analytic_accounts'):
    #         analytic_account_ids = [int(acc) for acc in options['analytic_accounts']]
    #         domain.append(('analytic_account_id', 'in', analytic_account_ids))
    #     if options.get('analytic_tags'):
    #         analytic_tag_ids = [int(tag) for tag in options['analytic_tags']]
    #         domain.append(('analytic_tag_ids', 'in', analytic_tag_ids))
    #     if options.get('analytic_group'):
    #         analytic_group_ids = [int(gro) for gro in options['analytic_group_ids']]
    #         domain.append(('analytic_group', 'in', analytic_group_ids))

    #         # domain += [('analytic_group', 'in', options.get('analytic_group_ids'))]
    #     print("... .. .. .     ",domain)
    #     return domain

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('analytic_group_ids'):
            analytic_group_ids = self.env['account.analytic.group'].browse([int(ag) for ag in options.get('analytic_group_ids', [])])
            ctx['analytic_group_ids'] = analytic_group_ids.ids
        
        if options.get('operating_unit_ids'):
            operating_unit_ids = self.env['operating.unit'].browse([int(ou) for ou in options.get('operating_unit_ids', [])])
            ctx['operating_unit_ids'] = operating_unit_ids.ids

        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        info = super(AccountReport, self).get_report_informations(options)
        if options and options.get('analytic_group'):
            options['selected_analytic_group_ids'] = [self.env['account.analytic.group'].browse(int(ag)).name for ag in options.get('analytic_group_ids', [])]

        if options and options.get('operating_unit_id'):
            options['selected_operating_unit_ids'] = [self.env['operating.unit'].browse(int(ou)).name for ou in options.get('operating_unit_ids', [])]
        return info
