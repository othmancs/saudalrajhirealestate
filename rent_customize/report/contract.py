# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime, time


class ContractWizard(models.TransientModel):
    _name = 'contract.wizard'
    _rec_name = 'start_date'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def show_report(self):
        action = self.env.ref("rent_customize.filter_dates_action").read()[0]
        # print(datetime.combine(self.start_date, time.min))
        # print(datetime.combine(self.end_date, time.max))
        contract_ids = self.env['sale.order'].search([
            ('is_rental_order', '=', True),
            ('fromdate', '>=', self.start_date),
            ('todate', '<=', self.end_date),
        ])
        action["domain"] = [("id", "in", contract_ids.ids)]
        # return action

        tree_view_id = self.env.ref('rent_customize.contract_view_tree').ids
        form_view_id = self.env.ref('sale_renting.rental_order_primary_form_view').ids
        return {
            'domain': [('id', 'in', contract_ids.ids)],
            'name': 'Rental Contract From %s to %s'%(self.start_date , self.end_date ),
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }