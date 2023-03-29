# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

INSURANCE_ADMIN_FEES_PRODUCTS = ['insurance_value', 'contract_admin_fees', 'contract_service_fees',
                                 'contract_admin_sub_fees', 'contract_service_sub_fees']
INSURANCE_ADMIN_FEES_FIELDS = ['insurance_value', 'contract_admin_fees', 'contract_service_fees',
                               'contract_admin_sub_fees', 'contract_service_sub_fees']


class RentSaleInvoices(models.Model):
    _name = 'rent.sale.invoices'

    sale_order_id = fields.Many2one('sale.order', copy=True, string='العقود', ondelete='cascade')
    name = fields.Char(string='Label')
    sequence = fields.Integer(string='Sequence')
    amount = fields.Float(string='Amount')
    invoice_date = fields.Date(string='Invoice Date')
    status = fields.Selection([('uninvoiced', 'Un Invoiced'), ('invoiced', 'Invoiced')], string='Status',
                              default="uninvoiced")
    fromdate = fields.Datetime(string='From Date', default=fields.Date.context_today, copy=False, required=True)
    todate = fields.Datetime(string='To Date', default=fields.Date.context_today, copy=False, required=True)
    operating_unit = fields.Many2one('operating.unit', string='Operating Unit',
                                     related='sale_order_id.operating_unit_id')

    def _prepare_invoice_line(self, line):
        self.ensure_one()
        res = {
            'display_type': line.display_type,
            'sequence': line.sequence,
            'name': line.name,
            'product_id': line.product_id.id,
            'product_uom_id': line.product_uom.id,
            'quantity': 1,
            'discount': line.discount,
            'price_unit': line.price_unit / self.sale_order_id.invoice_number,
            'tax_ids': [(6, 0, line.tax_id.ids)],
            'analytic_account_id': line.product_id.analytic_account.id,
            'sale_line_ids': [(4, line.id)],
            'exclude_from_invoice_tab': False,
        }
        # 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
        if self.sequence == 1:
            res.update({
                # 'property_price_unit': line.price_unit / self.sale_order_id.invoice_number,
                # 'price_unit': (line.price_unit / self.sale_order_id.invoice_number) + line.contract_admin_sub_fees + line.contract_service_sub_fees,
                'price_unit': (line.price_unit / self.sale_order_id.invoice_number),
                # 'insurance_value': line.insurance_value,
                # 'contract_admin_fees': line.contract_admin_fees,
                # 'contract_service_fees': line.contract_service_fees,
                # 'contract_admin_sub_fees': line.contract_admin_sub_fees,
                # 'contract_service_sub_fees': line.contract_service_sub_fees
            })
        return res

    def _prepare_invoice_line_insurance_admin_fees_sum(self, type, seq):
        self.ensure_one()
        res = {}
        type_name = 'renting.' + type
        type_config_parameter = self.env['ir.config_parameter'].sudo().get_param(type_name)
        type_product_template = self.env['product.template'].search([('id', '=', int(type_config_parameter))])
        if not type_product_template:
            raise UserError(_('Please define Insurance and admin fees products in renting setting.'))
        fees_amount = 0
        fees_amount = sum(self.sale_order_id.order_line.mapped(type))
        if fees_amount > 0:
            res = {
                'display_type': 'line_note',
                'sequence': seq + 1000,
                'name': 'إجمالي قيمة ' + type_product_template.name + ': ' + str(fees_amount),
                'exclude_from_invoice_tab': False,
            }
        else:
            res = {
                'name': False,
            }
        return res

    def _prepare_invoice_line_insurance_admin_fees(self, type, line, seq):
        self.ensure_one()
        type_name = 'renting.' + type
        type_config_parameter = self.env['ir.config_parameter'].sudo().get_param(type_name)
        type_product_template = self.env['product.template'].search([('id', '=', int(type_config_parameter))])
        if not type_product_template:
            raise UserError(_('Please define Insurance and admin fees products in renting setting.'))
        fees_amount = line.mapped(type)[0]
        res = {
            'sequence': seq + 1000,
            'name': type_product_template.name,
            'product_id': type_product_template.id,
            'product_uom_id': 1,
            'quantity': 1,
            'price_unit': fees_amount,
            'analytic_account_id': line.product_id.analytic_account.id,
            'tax_ids': [(6, 0, self.sale_order_id.order_line.tax_id.ids)] if type in ['contract_admin_sub_fees',
                                                                                      'contract_service_sub_fees'] else False,
            'exclude_from_invoice_tab': False,
            'rent_fees': True,
            # 'sale_line_ids': [(4, line.id)],
        }
        return res

    def _prepare_invoice(self, invoice_lines):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.sale_order_id.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.sale_order_id.note,
            'rent_sale_line_id': self.id,
            'currency_id': self.sale_order_id.pricelist_id.currency_id.id,
            'campaign_id': self.sale_order_id.campaign_id.id,
            'medium_id': self.sale_order_id.medium_id.id,
            'source_id': self.sale_order_id.source_id.id,
            'user_id': self.sale_order_id.user_id.id,
            'invoice_user_id': self.sale_order_id.user_id.id,
            'team_id': self.sale_order_id.team_id.id,
            'partner_id': self.sale_order_id.partner_invoice_id.id,
            'partner_shipping_id': self.sale_order_id.partner_shipping_id.id,
            'fiscal_position_id': (
                    self.sale_order_id.fiscal_position_id or self.sale_order_id.fiscal_position_id.get_fiscal_position(
                self.sale_order_id.partner_invoice_id.id)).id,
            'partner_bank_id': self.sale_order_id.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.sale_order_id.name,
            'invoice_payment_term_id': self.sale_order_id.payment_term_id.id,
            'payment_reference': self.sale_order_id.reference,
            'transaction_ids': [(6, 0, self.sale_order_id.transaction_ids.ids)],
            "invoice_line_ids": invoice_lines,
            'company_id': self.sale_order_id.company_id.id,
            'operating_unit_id': self.operating_unit.id,
            'fromdate': self.fromdate,
            'todate': self.todate,
        }
        return invoice_vals

    def create_invoices(self):
        invoice_lines = []
        invoiceable_lines = self.sale_order_id.order_line
        if self.sequence == 1:
            seq = 0
            for type in INSURANCE_ADMIN_FEES_FIELDS:
                seq += 1
                fees_sum = self._prepare_invoice_line_insurance_admin_fees_sum(type, seq)
                if fees_sum.get('name', False):
                    invoice_lines.append([0, 0, fees_sum])
        for line in invoiceable_lines:
            invoice_lines.append([0, 0, self._prepare_invoice_line(line)])
            if self.sequence == 1:
                seq = 0
                for type in INSURANCE_ADMIN_FEES_FIELDS:
                    seq += 1
                    if line.mapped(type)[0] > 0:
                        invoice_lines.append([0, 0, self._prepare_invoice_line_insurance_admin_fees(type, line, seq)])

        vals = self._prepare_invoice(invoice_lines)
        print(vals)
        invoice = self.env['account.move'].create(vals)
        self.invoice_date = fields.Date.today()
        self.status = 'invoiced'
        return invoice


class RentSaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    insurance_value = fields.Many2one('product.template', string='التأمين', config_parameter="renting.insurance_value")
    contract_admin_fees = fields.Many2one('product.template', string='رسوم ادارية',
                                          config_parameter="renting.contract_admin_fees")
    contract_service_fees = fields.Many2one('product.template', string='رسوم الخدمات',
                                            config_parameter="renting.contract_service_fees")
    contract_admin_sub_fees = fields.Many2one('product.template', string='رسوم ادارية خاضعة',
                                              config_parameter="renting.contract_admin_sub_fees")
    contract_service_sub_fees = fields.Many2one('product.template', string='رسوم الخدمات خاضعة',
                                                config_parameter="renting.contract_service_sub_fees")


class RentSalestats(models.Model):
    _name = 'rent.sale.state'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    sale_order = fields.Many2one('sale.order', string='Sale Order')
    sale_order_line_id = fields.Many2one('sale.order.line', string='الوحدة', domain="[('order_id', '=', sale_order)]")
    # product_id = fields.Many2one('product.template', string='الوحدة')
    sequence = fields.Integer(string='Sequence')

    door_good = fields.Boolean('جيد')
    door_bad = fields.Boolean('سئ')
    door_comment = fields.Char('حدد')
    wall_good = fields.Boolean('جيد')
    wall_bad = fields.Boolean('سئ')
    wall_comment = fields.Char('حدد')
    window_good = fields.Boolean('جيد')
    window_bad = fields.Boolean('سئ')
    window_comment = fields.Char('حدد')
    water_good = fields.Boolean('جيد')
    water_bad = fields.Boolean('سئ')
    water_comment = fields.Char('حدد')
    elec_good = fields.Boolean('جيد')
    elec_filter = fields.Char('تصفية عداد الكهرباء')
    water_filter = fields.Char('تصفية عداد المياه')
    elec_bad = fields.Boolean('سئ')
    elec_comment = fields.Char('حدد')
    rdoor_good = fields.Boolean('جيد')
    rdoor_bad = fields.Boolean('سئ')
    rdoor_comment = fields.Char('حدد')
    rwall_good = fields.Boolean('جيد')
    rwall_bad = fields.Boolean('سئ')
    rwall_comment = fields.Char('حدد')
    rwindow_good = fields.Boolean('جيد')
    rwindow_bad = fields.Boolean('سئ')
    rwindow_comment = fields.Char('حدد')
    rwater_good = fields.Boolean('جيد')
    rwater_bad = fields.Boolean('سئ')
    rwater_comment = fields.Char('حدد')
    relec_good = fields.Boolean('جيد')
    relec_bad = fields.Boolean('سئ')
    relec_comment = fields.Char('حدد')
    relec_filter = fields.Char('تصفية عداد الكهرباء')
    rwater_filter = fields.Char('تصفية عداد المياه')
    customer_accept = fields.Boolean('نعم')
    customer_refused = fields.Boolean('لا')
    notes = fields.Text('الملاحظات')
    rnotes = fields.Text('الملاحظات')
    mangement_accept = fields.Boolean('نعم')
    mangement_refused = fields.Boolean('لا')
    manage_note = fields.Text('ملاحظة')
    rmanage_note = fields.Text('ملاحظة')
    is_cost = fields.Boolean('نعم')
    is_no_cost = fields.Boolean('لا')
    is_amount_rem = fields.Boolean('نعم')
    is_no_amount_rem = fields.Boolean('لا')
    amount_rem = fields.Float('المبلغ المتبقي')
    iselec_remain = fields.Boolean('نعم')
    isnotelec_remain = fields.Boolean('لا')
