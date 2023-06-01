# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_analytic_group = None
    filter_operation = None
    filter_building = None
    filter_property = None


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

        if not self.filter_building:
            return options
        options['building_id'] = True
        options['building_ids'] = previous_options and previous_options.get('building_ids') or []
        selected_building_ids = [int(partner) for partner in options['building_ids']]
        selected_building = selected_building_ids and self.env['rent.property.build'].browse(selected_building_ids) or self.env['rent.property.build']
        options['selected_building_ids'] = selected_building.mapped('name')

        if not self.filter_property:
            return options
        options['property_id'] = True
        options['property_ids'] = previous_options and previous_options.get('property_ids') or []
        selected_property_ids = [int(partner) for partner in options['property_ids']]
        selected_property = selected_property_ids and self.env['rent.property'].browse(selected_property_ids) or self.env['rent.property']
        options['selected_property_ids'] = selected_property.mapped('property_name')

        return options
    
    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountReport, self)._get_options(previous_options)
        self._init_analytic_group(options, previous_options)
        self._init_operation(options, previous_options)

        return options
    

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('analytic_group_ids'):
            analytic_group_ids = self.env['account.analytic.group'].browse([int(ag) for ag in options.get('analytic_group_ids', [])])
            ctx['analytic_group_ids'] = analytic_group_ids.ids
        
        if options.get('operating_unit_ids'):
            operating_unit_ids = self.env['operating.unit'].browse([int(ou) for ou in options.get('operating_unit_ids', [])])
            ctx['operating_unit_ids'] = operating_unit_ids.ids
        if options.get('building_ids'):
            building_ids = self.env['rent.property.build'].browse([int(ou) for ou in options.get('building_ids', [])])
            ctx['building_ids'] = building_ids.ids
        if options.get('property_ids'):
            ctx['property_ids'] = self.env['rent.property'].browse([int(ou) for ou in options.get('property_ids', [])]).ids

        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        info = super(AccountReport, self).get_report_informations(options)
        if  options and options.get('analytic_group') is not None:
            options['selected_analytic_group_ids'] = [self.env['account.analytic.group'].browse(int(ag)).name for ag in options.get('analytic_group_ids', [])]
        if  options and options.get('operating_unit_ids') is not None:
            options['selected_operating_unit_ids'] = [self.env['operating.unit'].browse(int(ou)).name for ou in options.get('operating_unit_ids', [])]
        if  options and options.get('building_ids') is not None:
            options['selected_building_ids'] = [self.env['rent.property.build'].browse(int(ou)).name for ou in options.get('building_ids', [])]
        if  options and options.get('property_ids') is not None:
            options['selected_property_ids'] = [self.env['rent.property'].browse(int(ou)).property_name for ou in options.get('property_ids', [])]
        return info
