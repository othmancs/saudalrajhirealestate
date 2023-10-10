from odoo import fields, models,api
from odoo import tools
from datetime import timedelta


PAYMENT_STATE_SELECTION = [
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
]


class ContractReminderReport(models.Model):
    _name = "contract.reminder.report"
    _description = "Contract Reminder Report"
    _auto = False
    _rec_name = 'contract_id'

    company_id = fields.Many2one("res.company", "Company", readonly=True)
    contract_id = fields.Many2one("sale.order", "Ref", readonly=True)
    contract_number = fields.Char("Contract Number", readonly=True)
    property_id = fields.Many2one("rent.property", "Property", readonly=True)
    customer_id = fields.Many2one("res.partner", "Customer", readonly=True)
    amount = fields.Float("Amount", readonly=True, digits='Product Unit of Measure')
    paid_amount = fields.Float("Paid Amount", readonly=True, digits='Product Unit of Measure')
    contract_start_date = fields.Date("Contract Start Date", readonly=True)
    contract_end_date = fields.Date("Contract End Date", readonly=True)
    invoice_date = fields.Date("Invoice Date", readonly=True)
    invoice_date_due = fields.Date("Invoice Due Date", readonly=True)
    reminder_date = fields.Date("Reminder Date", readonly=True, compute="compute_reminder_date")
    product_id = fields.Many2one('product.product', string='Item')
    payment_state = fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status", store=True,
                                     readonly=True, copy=False, tracking=True, )

    @api.depends('contract_id', 'invoice_date')
    def compute_reminder_date(self):
        for record in self:
            days  = self.env['ir.config_parameter'].get_param('rent_customize.invoice_notify')
            record.reminder_date = record.invoice_date + timedelta(days=int(days))

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        query = """
       SELECT
        aml.id as id,so.id as contract_id,  aml.product_id as product_id,so.company_id as company_id,
         so.fromdate as contract_start_date, so.todate as contract_end_date,am.invoice_date_due::DATE as invoice_date_due,
        am.invoice_date::DATE as invoice_date, aml.price_subtotal as amount,pt.property_id as property_id,
        so.contract_number as contract_number,(aml.price_subtotal - aml.amount_residual) as paid_amount,
        am.payment_state as payment_state, am.partner_id as customer_id
        FROM account_move_line as aml
            JOIN account_move am ON (am.id = aml.move_id)
            JOIN rent_sale_invoices inv ON (inv.id = am.rent_sale_line_id)
            JOIN sale_order so ON (so.id = inv.sale_order_id)
            JOIN product_product pro ON (aml.product_id = pro.id)
            JOIN res_partner rp ON (so.partner_id = rp.id)
            LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
        WHERE so.rental_status  IN ('pickup', 'return') and so.is_rental_order = true
            """

        return query

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
