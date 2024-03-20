from odoo import fields, models, tools, api


class MoveLineReport(models.Model):
    _name = 'move.line.report.tree'
    _description = 'Move Line Report'
    _order = 'invoice_date desc'

    aml_id = fields.Many2one('account.move.line', 'Line')
    subtotal = fields.Float(string='Subtotal')
    paid = fields.Float(string='Paid')
    remaining = fields.Float(string='Remaining')
    product_id = fields.Many2one('product.product', 'Product', related='aml_id.product_id', store=1)
    label = fields.Char('Label', related='aml_id.name')
    analytic_account_id = fields.Many2one('account.analytic.account', related='aml_id.analytic_account_id', store=1)

    move_id = fields.Many2one('account.move', 'Invoice')
    company_id = fields.Many2one('res.company', related='move_id.company_id', store=1)
    customer_id = fields.Many2one('res.partner', 'Customer', related='move_id.partner_id', store=1)
    operating_unit_id = fields.Many2one('operating.unit', related='move_id.operating_unit_id', store=1)
    invoice_date = fields.Date('Invoice Date', related='move_id.invoice_date')
    rent_sale_line_id = fields.Many2one('rent.sale.invoices', related='move_id.rent_sale_line_id')
    journal_id = fields.Many2one('account.journal', related='move_id.journal_id', store=1)
