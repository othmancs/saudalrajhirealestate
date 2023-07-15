# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools


class ContractMasterData(models.Model):
    _name = 'contract.master.data'
    _auto = False

    property_number = fields.Many2one(comodel_name='rent.property', string='Property Number',readonly="1")
    product_id = fields.Many2one(comodel_name='product.product', string='Product',readonly="1")
    unit_area = fields.Float(string='Unit Area',readonly="1")
    unit_floor_number = fields.Char(string='Unit Floor Number',readonly="1")
    property_has_parking = fields.Boolean(string='Parking',readonly="1")
    furniture_bedroom_no = fields.Integer(string='Bedroom',readonly="1")
    furniture_bathroom_no = fields.Integer(string='Bathroom',readonly="1")
    living = fields.Integer(string='living',default=000,readonly="1")
    furniture_kitchen_installed = fields.Boolean(string='Kitchen Equipped',readonly="1")
    partner_id = fields.Many2one(comodel_name='res.partner', string='Tenant',readonly="1")
    contract = fields.Char(string='Contract',readonly="1")
    contract_number = fields.Char(string='Contract Number',readonly="1")
    name = fields.Char(string='Name',readonly="1")
    price_unit = fields.Float(string='Price Unit',readonly="1")
    contract_service_fees = fields.Float(string='Service',readonly="1")
    deposit = fields.Float(string='Deposit',readonly="1")
    price_tax = fields.Float(string='VAT',readonly="1")
    unit_electricity = fields.Char(string='Electricity',readonly="1")
    unit_water = fields.Char(string='Water',readonly="1")
    unit_gas = fields.Char(string='Gas',readonly="1")
    insurance_value = fields.Float(string='Insurance',readonly="1")
    fromdate = fields.Date(string='From Date',readonly="1")
    todate = fields.Date(string='To Date',readonly="1")
    installment_due = fields.Char(string='Installment Due',readonly="1")
    premium_due_with_insurance = fields.Char(string='premium due with insurance',readonly="1")
    new_due_date = fields.Char(string='New Due Date',readonly="1")
    indebtedness_due_date = fields.Char(string='Indebtedness due date',readonly="1")
    number_of_payment  = fields.Char(string='Number Of Payment',readonly="1")
    indebtedness_amount  = fields.Char(string='Indebtedness Amount',readonly="1")
    total_amount_with_trade_tax  = fields.Char(string='Total amount with trade tax',readonly="1")
    total_overdue_and_due  = fields.Char(string='Total Overdue and Due',readonly="1")
    contact_number = fields.Char(string='Contact Number',related="partner_id.mobile",readonly="1")
    id_number = fields.Char(string='ID Number',related="partner_id.national_id_number",readonly="1")
    date_o_birth = fields.Date(string='Date Of Birth',related="partner_id.date_o_birth",readonly="1")
    method_of_payment = fields.Char(string='Method of Payment',readonly="1")
    lift = fields.Char(string='Lift',readonly="1")
    balcony = fields.Char(string='Balcony',readonly="1")
    garden = fields.Char(string='Garden',readonly="1")
    garden_des = fields.Char(string='Garden Description',readonly="1")
    
    
    
    
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

    