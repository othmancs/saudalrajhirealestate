from odoo import models, fields, _


class RentalLetterTemplate(models.Model):
    _name = 'rental.letter.template'
    _description = 'Rental Letter Templates'

    name = fields.Char()
    subject = fields.Char(required=True)
    bank_id = fields.Many2one('res.bank', string='Bank')
    payment_period = fields.Char(string='Payment Period')
    bank_account = fields.Char(string='Bank Account')
    iban = fields.Char(string='IBAN')
    contract_date = fields.Date(string='Contract Date')
    unit_number = fields.Char(string='Unit Number')
    neighborhood = fields.Char(string='Neighborhood')
    contract_id = fields.Many2one('sale.order', domain=[('state', 'in', ['occupied', 'done'])])
    rental_value = fields.Float(string='Rental Value')
    new_rental_value = fields.Float(string='New Rental Value')
    new_contract_date = fields.Date(string='New Contract Date')
    eviction_period = fields.Char(string='Eviction Period')
    daily_rent_value = fields.Float(string='Daily Rent Value')
    location = fields.Char(string='Location')
    property_type = fields.Char(string='Property Type')
    change_reason = fields.Char(string='Change Reason')
    partner_id = fields.Many2one(string='Customer')
    identity = fields.Char(string='Identity')
    contact_number = fields.Char(string='Contact Number')
    employer = fields.Char(string='Employer')
    job = fields.Char(string='Job')
    salary_definition = fields.Char(string='Salary Definition')
    martial_status = fields.Char(string='Martial Status')
    family_members = fields.Integer(string='Family Members')
    simah_report = fields.Char(string='Simah Report')
    renting_purpose = fields.Char(string='Renting Purpose')
    nature_of_commerce = fields.Char(string='Nature of commerce')
    manager = fields.Char(string='Commissioner Director')
    manager_identity = fields.Char(string='Manager Identity')
    targeted_group = fields.Char(string='Targeted Group')
    invoice_ids = fields.Many2many('rent.due.invoice', 'letter_template_id', string='Due Invoices')


class RentDueInvoice(models.Model):
    _name = 'rent.due.invoice'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    amount = fields.Float(string='Amount')
    tax_amount = fields.Float(string='Tax Amount')
    letter_template_id = fields.Many2one('rental.letter.template')
