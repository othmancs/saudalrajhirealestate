from odoo import fields, models, api


class MaintenanceRequestExpense(models.Model):
    _name = 'maintenance.request.expense'
    _description = 'Property Maintenance Request Expense'

    maintenance_request_id = fields.Many2one('maintenance.request')
    partner_id = fields.Many2one("res.partner", string="Vendor", required=1)
    product_id = fields.Many2one("product.product",
                                 required=1,
                                 domain=[('partner_id', '=', False)])
    quantity = fields.Float("Quantity", required=1)
    tax_ids = fields.Many2many("account.tax", string="Taxes", domain=[('type_tax_use', '=', 'purchase')])
    price_unit = fields.Float("Price", digits='Product Price', required=1)

    def _prepare_invoice_line(self):
        self.ensure_one()
        res = {
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'analytic_account_id': self.maintenance_request_id.property_id.analytic_account.id or False,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'tax_ids': self.tax_ids.ids,
        }
        return res
