# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools


class ContractMasterData(models.Model):
    _name = 'contract.master.data'
    _auto = False

    property_number = fields.Many2one(comodel_name='rent.property', string='Property Number')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    unit_area = fields.Float(string='Unit Area')
    unit_floor_number = fields.Char(string='Unit Floor Number')
    property_has_parking = fields.Boolean(string='Parking')
    furniture_bedroom_no = fields.Integer(string='Bedroom')
    furniture_bathroom_no = fields.Integer(string='Bathroom')
    living = fields.Integer(string='living',default=000)
    furniture_kitchen_installed = fields.Boolean(string='Kitchen Equipped')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Tenant')
    contract = fields.Char(string='Contract')
    contract_number = fields.Char(string='Contract Number')
    name = fields.Char(string='Name')
    price_unit = fields.Float(string='Price Unit')
    contract_service_fees = fields.Float(string='Service')
    deposit = fields.Float(string='Deposit')
    price_tax = fields.Float(string='VAT')
    unit_electricity = fields.Char(string='Electricity')
    unit_water = fields.Char(string='Water')
    unit_gas = fields.Char(string='Gas')
    insurance_value = fields.Float(string='Insurance')
    fromdate = fields.Date(string='From Date')
    todate = fields.Date(string='To Date')

    installment_due = fields.Char(string='Installment Due',)
    premium_due_with_insurance = fields.Char(string='premium due with insurance',)
    new_due_date = fields.Char(string='New Due Date',)
    indebtedness_due_date = fields.Char(string='Indebtedness due date',)
    number_of_payment  = fields.Char(string='Number Of Payment',)
    indebtedness_amount  = fields.Char(string='Indebtedness Amount',)
    total_amount_with_trade_tax  = fields.Char(string='Total amount with trade tax',)
    total_overdue_and_due  = fields.Char(string='Total Overdue and Due',)
    contact_number = fields.Char(string='Contact Number',related="partner_id.mobile",)
    id_number = fields.Char(string='ID Number',related="partner_id.national_id_number")
    date_o_birth = fields.Date(string='Date Of Birth',related="partner_id.date_o_birth")
    method_of_payment = fields.Char(string='Method of Payment',)
    
    lift = fields.Char(string='Lift')
    balcony = fields.Char(string='Balcony')
    garden = fields.Char(string='Garden')
    garden_des = fields.Char(string='Garden Description')
    
    
    
    
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        q = """
        
        select 
        sol.id,
        sol.property_number,
        sol.product_id,
        pt.unit_area,
        pt.unit_floor_number,
        rp.property_has_parking,
        pt.furniture_bedroom_no,
        pt.furniture_bathroom_no,
        pt.furniture_bathroom_no as living,
        pt.furniture_kitchen_installed,

        so.partner_id,
        'contract' as contract,
        so.contract_number,
        so.name,
        sol.price_unit,
        sol.contract_service_fees,
        0.0 as deposit,
        sol.price_tax,
        pt.unit_electricity,
        pt.unit_water,
        pt.unit_gas,
        sol.insurance_value,
        so.fromdate,
        so.todate,

        'None' as installment_due,
        'None' as premium_due_with_insurance,
        'None' as new_due_date,
        'None' as indebtedness_due_date,
        'None' as number_of_payment,
        'None' as indebtedness_amount,
        'None' as total_amount_with_trade_tax,
        'None' as total_overdue_and_due,
        'None' as contact_number,
        'None' as id_number,
        'None' as date_o_birth,
        'None' as method_of_payment,
        'None' as lift,
        'None' as balcony,
        'None' as garden,
        'None' as garden_des
	
    from
        sale_order_line as sol
        left join sale_order so on (so.id = sol.order_id)
        left join product_product p on (sol.product_id = p.id )
        left join product_template pt on (p.product_tmpl_id = pt.id )
        left join rent_property rp on (sol.property_number = rp.id)

        """
        return q

    