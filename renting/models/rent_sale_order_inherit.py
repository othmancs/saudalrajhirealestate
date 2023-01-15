# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_number = fields.Char(string='رقم العقد')
    fromdate = fields.Datetime(string='From Date', default=datetime.today(), copy=False, required=True)
    todate = fields.Datetime(string='To Date', default=datetime.today(), copy=False, required=True)
    # Fields in Contract Info Tab
    order_contract = fields.Binary(string='العقد')
    invoice_terms = fields.Selection(
        [('monthly', 'شهري'), ('qua-year', '3 شهور'), ('half-year', '6 أشهر'), ('year', 'سنوي')],
        string='Invoice Terms',
        default='monthly')
    order_contract_invoice = fields.One2many('rent.sale.invoices', 'sale_order_id', string='العقد')
    contract_total_payment = fields.Float(string='Total Contract')
    contract_total_fees = fields.Float(string='Total Fees')
    brand_nameplate_allowed = fields.Boolean(string='Nameplate Allowed')
    contract_hegira_date = fields.Char(string='التاريخ الهجري')
    contract_penalties = fields.Float(string='الجزائات')
    contract_extra_maintenance_cost = fields.Float(string='تكلفة الصيانة الاضافية')
    contractor_pen = fields.Char(string='رسوم متأخرات')
    amount_remain = fields.Float(string='اجمالي المتبقي', compute='_get_remain')
    invoice_number = fields.Integer(string='Number Of Invoices')
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    order_property_state = fields.One2many('rent.sale.state', 'sale_order_id', string='الحالة')

    # بنود الاستلام
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

    def _get_remain(self):
        amount = 0
        invoices_paid = self.env['account.move'].sudo().search(
            [('invoice_origin', '=', self.name), ('payment_state', 'in', ['paid', 'in_payment'])])
        for line in invoices_paid:
            print(line)
            amount += line.amount_total
        self.amount_remain = self.amount_total - amount

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                # fees_price = 0.0 fees_price = line.price_subtotal + line.insurance_value + line.contract_admin_fees
                # + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def create_order_invoices(self):
        for rec in self:
            if rec.invoice_number <= 0:
                raise UserError(_('من فضلك اكتب عدد الفواتير'))
            rec.order_contract_invoice = False
            fromdate = rec.fromdate
            d1 = fields.Datetime.from_string(rec.fromdate)
            d2 = fields.Datetime.from_string(rec.todate)
            total_contract_period = d2 - d1

            if total_contract_period.days <= 0:
                raise UserError(_('يجب اختيار مدة العقد بصورة صحيحة'))

            diff = 0
            diff = total_contract_period.days / rec.invoice_number
            diff = round(diff, 0)
            # if abs(total_contract_period.days) % abs(rec.invoice_number) >0:
            #     raise UserError(_('يجب كتابة عدد فواتير مناسب لمدة العقد'))
            #

            for i in range(1, rec.invoice_number + 1):

                total_other_amount = sum((i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
                                         for i in rec.order_line)
                taxed_total_other_amount = sum((i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in rec.order_line)

                total_property_amount_without_tax = sum((i.product_uom_qty * i.price_unit) for i in rec.order_line)

                property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number

                total_tax_first_inv = sum((property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in rec.order_line.tax_id )
                total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id )

                todate = fromdate + relativedelta(days=diff)

                if i == 1:
                    amount = property_amount_per_inv + total_other_amount + total_tax_first_inv
                if i == rec.invoice_number:
                    amount = total_property_amount_without_tax - sum(rec.order_contract_invoice.mapped('amount'))
                else:
                    amount = property_amount_per_inv + total_tax
                if amount > 0:
                    sale_invoices = self.env['rent.sale.invoices'].create({
                        'name': "فاتورة رقم " + str(i),
                        'sequence': i,
                        'fromdate': fromdate,
                        'todate': rec.todate if rec.invoice_number == i else todate,
                        'amount': amount,
                        'sale_order_id': rec.id,
                    })
                fromdate = todate + relativedelta(days=1)

    @api.onchange("fromdate", "todate")
    def onchang_contract_dates(self):
        self.get_invoice_number()

    def get_invoice_number(self):
        diff = relativedelta(self.todate, self.fromdate)
        m = month = 0
        if diff.years != 0:
            m = diff.years * 12
        if diff.months != 0:
            month = diff.months
        self.invoice_number = month + m

    def action_confirm(self):
        if self.invoice_number == 0:
            # self.get_invoice_number()
            raise UserError(_('من فضلك اكتب عدد الفواتير'))
        result = super(RentSaleOrder, self).action_confirm()
        if self.is_rental_order:
            self.create_order_invoices()
        return result

    full_invoiced = fields.Boolean(string="Fully Invoiced", compute="_compute_full_invoiced", store=True)
    no_of_invoiced = fields.Integer(string="عدد الفواتير المفوترة", compute="compute_no_invoiced", store=True)
    no_of_not_invoiced = fields.Integer(string="عدد الفواتير الغير مفوترة", compute="compute_no_invoiced", store=True)
    no_of_invoiced_amount = fields.Float(string="المبالغ المفوترة", compute="compute_no_invoiced", store=True)
    no_of_not_invoiced_amount = fields.Float(string="المبالغ الغير مفوترة", compute="compute_no_invoiced", store=True)

    @api.depends('order_contract_invoice.status','order_contract_invoice.amount')
    def compute_no_invoiced(self):
        for order in self:
            order.no_of_invoiced = 0
            order.no_of_not_invoiced = 0
            order.no_of_invoiced_amount = 0
            order.no_of_not_invoiced_amount = 0
            order.no_of_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced'))
            order.no_of_invoiced_amount = sum(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced').mapped('amount'))
            order.no_of_not_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced'))
            order.no_of_not_invoiced_amount = sum(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced').mapped('amount'))

    @api.depends('order_contract_invoice.status')
    def _compute_full_invoiced(self):
        for order in self:
            order.full_invoiced = False
            not_invoiced = order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced')
            if not not_invoiced and len(order.order_contract_invoice) > 0:
                order.full_invoiced = True

    @api.model
    def create(self, vals):
        result = super(RentSaleOrder, self).create(vals)
        if result.invoice_number <= 0 and result.is_rental_order:
            raise UserError(_('من فضلك اكتب عدد الفواتير'))
        return result

    # @api.model_create_multi
    # def create(self, vals_list):
    #     order_lines_list = []
    #     res = super(RentSaleOrder, self).create(vals_list)
    #
    #     # if res.invoice_terms == 'monthly':
    #     #
    #     # elif res.invoice_terms == 'half-year':
    #     # elif res.invoice_terms == 'qua-year':
    #     # elif res.invoice_terms == 'year':
    #     product_admin = self.env['product.template'].sudo().search([('name', '=', 'رسوم ادارية')])
    #     product_admin.list_price = res.contract_admin_fees
    #     product_admin.standard_price = res.contract_admin_fees
    #     product_product_admin = self.env['product.product'].sudo().search([('product_tmpl_id', '=', product_admin.id)])
    #     if res.contract_admin_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم ادارية',
    #             'product_id': product_product_admin.id,
    #             'price_unit': res.contract_admin_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_admin_fees
    #         }))
    #     product_service = self.env['product.template'].sudo().search([('name', '=', 'رسوم خدمات')])
    #     product_service.list_price = res.contract_service_fees
    #     product_service.standard_price = res.contract_service_fees
    #     product_product_service = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_service.id)])
    #     if res.contract_service_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم خدمات',
    #             'product_id': product_product_service.id,
    #             'price_unit': res.contract_service_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_service_fees
    #         }))
    #     product_sub_admin = self.env['product.template'].sudo().search([('name', '=', 'رسوم ادارية خاضعة')])
    #     product_sub_admin.list_price = res.contract_admin_sub_fees
    #     product_sub_admin.standard_price = res.contract_admin_sub_fees
    #     product_product_sub_admin = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_sub_admin.id)])
    #     if res.contract_admin_sub_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم ادارية خاضعة',
    #             'product_id': product_product_sub_admin.id,
    #             'price_unit': res.contract_admin_sub_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_admin_sub_fees
    #         }))
    #     product_sub_service = self.env['product.template'].sudo().search([('name', '=', 'رسوم خدمات خاضعة')])
    #     product_sub_service.list_price = res.contract_service_sub_fees
    #     product_sub_service.standard_price = res.contract_service_sub_fees
    #     product_product_sub_service = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_sub_service.id)])
    #     if res.contract_service_sub_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم خدمات خاضعة',
    #             'product_id': product_product_sub_service.id,
    #             'price_unit': res.contract_service_sub_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_service_sub_fees
    #         }))
    #     product_service = self.env['product.template'].sudo().search([('name', '=', 'تـأمين')])
    #     product_service.list_price = res.insurance_value
    #     product_service.standard_price = res.insurance_value
    #     product_product_service = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_service.id)])
    #
    #     if res.insurance_value > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'تـأمين',
    #             'product_id': product_product_service.id,
    #             'price_unit': res.insurance_value,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.insurance_value
    #         }))
    #     print(order_lines_list)
    #     res.update({
    #
    #         'order_line': order_lines_list
    #
    #     })
    #
    #     return res


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    property_number = fields.Many2one('rent.property', string='العقار')
    pickup_date = fields.Datetime(string="Pickup", related='order_id.fromdate', store=True)
    return_date = fields.Datetime(string="Return", related='order_id.todate', store=True)
    insurance_value = fields.Float(string='قيمة التأمين')
    contract_admin_fees = fields.Float(string='رسوم ادارية')
    contract_service_fees = fields.Float(string='رسوم الخدمات')
    contract_admin_sub_fees = fields.Float(string='رسوم ادارية خاضعة')
    contract_service_sub_fees = fields.Float(string='رسوم الخدمات خاضعة')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit + line.insurance_value + line.contract_admin_fees + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
                    1 - (line.discount or 0.0) / 100.0)
            price_tax = line.price_unit + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
                    1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price_tax, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': price,
                # 'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

