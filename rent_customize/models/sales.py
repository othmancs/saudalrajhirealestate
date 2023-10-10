# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from odoo import models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from dateutil.relativedelta import relativedelta

from hijri_converter import Gregorian, convert


class RentalOrder(models.TransientModel):
    _inherit = 'rental.order.wizard'

    def apply(self):
        res = super(RentalOrder, self).apply()
        for rec in self:
            if rec.status == 'return':
                rec.order_id.state = 'termination'
                for line in rec.order_id.order_line:
                    line.product_id.unit_rented = False
                rec.order_id.rental_status = 'returned'
                for line in rec.rental_wizard_line_ids:
                    letter_id = self.env['rental.letter.template'].search([('subject', '=', 'eviction'),
                                                                           ('unit_id','=' ,line.order_line_id.id)])
                    if letter_id:
                        letter_id.write({'eviction_state': 'done'})
            if rec.status == 'pickup':
                rec.order_id.state = 'occupied'
                for line in rec.order_id.order_line:
                    line.product_id.unit_rented = True
                rec.order_id.rental_status = 'pickup'
        return res


class RentLog(models.Model):
    _name = "rent.log"
    order_id = fields.Many2one('sale.order')
    rent_id = fields.Many2one('sale.order')
    fromdate = fields.Date('From Date')
    todate = fields.Date('To Date')
    amount = fields.Float('Amount')


class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('review', 'To Review'),
        ('approve', 'Approved'),
        ('sale', 'Acceptance'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('occupied', 'Occupied'),
        ('termination', 'Termination'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    rental_status = fields.Selection(selection_add=[('review', 'To Review'), ('approve', 'To Approve'),
                                                    ('sent',)],
                                     ondelete={'review': 'set draft', 'approve': 'set draft'})
    apartment_insurance = fields.Float('Apartment Insurance')
    refund_insurance = fields.Boolean('Refund Insurance')
    damage_amount = fields.Float('Damage Amount')
    refund_amount = fields.Float('Refund Amount')
    context_order = fields.Many2one('sale.order')
    old_rent_ids = fields.One2many(comodel_name='rent.log', inverse_name='order_id', string='Old Rents')

    transfer_context_order = fields.Many2one('sale.order', copy=False)
    new_rental_id = fields.Many2one('sale.order', copy=False)
    transferred_id = fields.Many2one('sale.order', copy=False)
    transfer_customer_id = fields.Many2one('res.partner', 'Custoemr To Transfer', copy=False)
    transfer_date = fields.Date('Transfer Date', copy=False)
    transferred = fields.Boolean('Transferred ?', copy=False)
    annual_increase = fields.Boolean('Annual Increase ?')
    annual_increase_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed amount')
    ], default='percentage', string='Annual Increase Type')
    annual_amount = fields.Float("Annual Amount")
    product_id = fields.Many2one('product.product', string='Unit')
    product_ids = fields.Many2many('product.product', string='Unit_ids')
    letter_ids = fields.One2many('rental.letter.template', inverse_name='assigner_id',
                                 string='letters')
    letter_count = fields.Integer(compute="get_letter_count")

    @api.depends('letter_ids')
    def get_letter_count(self):
        for rec in self:
            rec.letter_count = len(rec.letter_ids.ids)

    def action_open_letters(self):
        action = self.env.ref("rent_customize.rent_letter_template").sudo().read()[0]
        action["domain"] = [("id", "in", self.letter_ids.ids)]
        action["context"] = {'default_assigner_id': self.id}
        return action


    @api.onchange("order_line")
    def _compute_allowed_products(self):
        product_ids = []
        for rec in self.order_line:
            print("00 00      ", rec)
            product_ids.append(self.env['product.product'].search([('id', '=', rec.product_id.id)]).id)

            print(".. ..    ", product_ids)
        self.product_ids = product_ids
        
    
    def action_submit(self):
        if not self.order_line:
            raise ValidationError(_("You need to add at least one line before Submitting."))
        return self.write({'state': 'review'})

    def action_review(self):
        return self.write({'state': 'approve'})

    def get_date_hijri(self, date):
        if date:
            day = date.day
            month = date.month
            year = date.year
            hijri_date = Gregorian(year, month, day).to_hijri()
            war_start = '2011-01-03'
            war = datetime.strptime(war_start, '%Y-%m-%d')
            war1 = convert.Gregorian.fromdate(war).to_hijri()
            return hijri_date

    def renew_contract(self):
        new_contract_id = self.copy()
        self.new_rental_id = new_contract_id.id
        fmt = '%Y-%m-%d'
        start_date = self.fromdate
        end_date = self.todate
        d1 = datetime.strptime(str(start_date)[:10], fmt)
        d2 = datetime.strptime(str(end_date)[:10], fmt)
        date_difference = d2 - d1
        new_contract_id.fromdate = self.todate
        new_contract_id.todate = new_contract_id.fromdate + relativedelta(days=date_difference.days)
        new_contract_id.invoice_number = self.invoice_number
        new_contract_id.is_rental_order = self.is_rental_order
        new_contract_id.partner_id = self.partner_id
        lines = []

        for line in self.order_line:

            annual_increase_amount = 0.0
            if self.annual_increase:
                if self.annual_increase_type == 'percentage':
                    annual_increase_amount = line.price_unit * self.annual_amount / 100
                else:
                    annual_increase_amount = self.annual_amount

            line = self.env['sale.order.line'].create({
                'order_id': new_contract_id.id,
                'property_number': line.property_number.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit + annual_increase_amount,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'insurance_value': line.insurance_value,
                'is_rental': line.is_rental,
                'contract_admin_fees': line.contract_admin_fees,
                'contract_service_fees': line.contract_admin_sub_fees,
                'contract_admin_sub_fees': line.contract_service_sub_fees,
            })
            lines.append(line.id)
        new_contract_id.order_line = [(6, 0, lines)]
        form_view_id = self.env.ref('sale_renting.rental_order_primary_form_view').ids
        for rent in self.old_rent_ids:
            self.env['rent.log'].create({
                'order_id': new_contract_id.id,
                'rent_id': rent.rent_id.id,
                'fromdate': rent.fromdate,
                'todate': rent.todate,
                'amount': rent.amount,
            })
        self.env['rent.log'].create({
            'order_id': new_contract_id.id,
            'rent_id': self.id,
            'fromdate': self.fromdate,
            'todate': self.todate,
            'amount': self.amount_total,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Renew Contract',
            'target': 'current',
            'res_model': 'sale.order',
            'res_id': new_contract_id.id,
            'view_id': form_view_id,  # optional
            'view_type': 'form',
            'views': [(form_view_id, 'form')],
        }

    @api.onchange('damage_amount', 'apartment_insurance')
    def change_damage_amount(self):
        self.refund_amount = self.apartment_insurance - self.damage_amount

    def action_termination(self):
        self.write({
            "rental_status": "returned",
            "state": "termination",
        })

    def action_refund_insurance(self):
        print(".. ..   ddddd ", self.product_ids)
        action = self.env.ref("rent_customize.refund_insurance_action").read()[0]
        action["views"] = [(self.env.ref("rent_customize.refund_insurance_view_form").id, "form") ]
        self.context_order = self.id
        self.apartment_insurance = self.apartment_insurance
        self.refund_amount = self.apartment_insurance
        self.state = self.state
        self.partner_invoice_id = self.partner_invoice_id.id
        self.partner_id = self.partner_id.id
        action["res_id"] = self.id
        return action

    
    def action_view_transfer(self):
        return {
            'name': _('Renting Order'),
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'create': False,
            'type': 'ir.actions.act_window',
            'res_id': self.new_rental_id.id,
        }

    def action_view_old_contract(self):

        return {
            'name': _('Renting Order'),
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'create': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.old_rent_ids.rent_id.ids)],
        }

    def action_view_transferred(self):
        # action = self.env.ref("sale_renting.rental_order_action").sudo().read()[0]
        return {
            'name': _('Renting Order'),
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'create': False,
            'type': 'ir.actions.act_window',
            'res_id': self.transferred_id.id,
        }

    def action_transfer(self):
        for rec in self:
            # uninvoiced = len(rec.order_contract_invoice.filtered(lambda ll: ll.status == 'uninvoiced').ids)
            # if uninvoiced <1:
            #     raise ValidationError(_("There is no draft invoice to be invoiced or transferred"))
            unpaid_invoices = len(
                rec.invoice_ids.filtered(lambda line: line.payment_state in ['not_paid', 'in_payment', 'partial']).ids)
            if unpaid_invoices > 0:
                raise ValidationError(_("There is unpaid invoices to be paid or reconciled!"))
            form_view_id = self.env.ref('rent_customize.transfer_view_form').ids
            return {
                'name': 'Transfer Apartment',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                # "context": {
                #     'default_partner_id': self.partner_id.id,
                #     'default_apartment_insurance': self.apartment_insurance,
                #     'default_refund_amount': self.apartment_insurance,
                #     'default_partner_invoice_id': self.partner_invoice_id.id,
                #     'default_partner_shipping_id': self.partner_shipping_id.id,
                #     'default_pricelist_id': self.pricelist_id.id,
                #     'default_transfer_context_order': self.id,
                #     'default_state': self.state,
                #     'default_company_id': self.company_id.id,
                #     'default_transfer_date': fields.Date.today(),
                # },
                'target': 'new',
            }

    def do_transfer(self):
        for rec in self:
            uninvoiced = len(rec.order_contract_invoice.filtered(lambda ll: ll.status == 'uninvoiced').ids)
            new_rental_id = rec.copy({
                'pricelist_id': rec.pricelist_id.id,
                'apartment_insurance': rec.pricelist_id.id,
                'fromdate': rec.transfer_date,
                'todate': rec.todate,
                'date_order': fields.Date.today(),
                'invoice_number': uninvoiced if uninvoiced > 0 else rec.invoice_number,
                'is_rental_order': True,
                'transferred_id': rec.id,
                'new_rental_id': False,
                'partner_id': rec.transfer_customer_id.id,
            })
            rec.new_rental_id = new_rental_id.id
            # print("XXXXXXXXXXrec.transfer_customer_id ",rec.transfer_customer_id)
            # rec.transfer_context_order.transfer_customer_id = rec.transfer_customer_id.id
            # rec.transfer_context_order.transfer_date = rec.transfer_date
            rec.transferred = True

    def do_transfer_and_print(self):
        for rec in self:
            rec.do_transfer()
            rec.print_transfer()

    def _prepare_refund_invoice_line(self):
        self.ensure_one()

        product_tmp_id = self.env['ir.config_parameter'].sudo().get_param('renting.insurance_value')
        product_id = self.env['product.product'].search([
            ('product_tmpl_id', '=', int(product_tmp_id))
        ])
        res = {
            'display_type': False,
            'name': product_id.name,
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'quantity': 1,
            'discount': 0,
            'price_unit': abs(self.refund_amount),
            'tax_ids': [(6, 0, [])],
            'sale_line_ids': [(4, self.context_order.order_line[0].id)],
            'analytic_account_id': self.product_id.product_tmpl_id.analytic_account.id,
            'exclude_from_invoice_tab': False,
        }
        return res

    def print_transfer(self):
        data = {
            'model': 'sale.order',
            'form': self.read()[0]
        }
        print("datadatadatadatadatadata", data)
        return self.env.ref('rent_customize.report_transfer_apratment').report_action(self)

    def _prepare_refund_invoices(self, sale_order_id, invoice_lines):
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
            'ref': sale_order_id.client_order_ref or '',
            'move_type': 'out_invoice' if self.refund_amount > 0 else 'out_refund',
            'narration': sale_order_id.note,
            'currency_id': sale_order_id.pricelist_id.currency_id.id,
            'campaign_id': sale_order_id.campaign_id.id,
            'medium_id': sale_order_id.medium_id.id,
            'source_id': sale_order_id.source_id.id,
            'user_id': sale_order_id.user_id.id,
            'invoice_user_id': sale_order_id.user_id.id,
            'team_id': sale_order_id.team_id.id,
            'partner_id': sale_order_id.partner_invoice_id.id if sale_order_id.partner_invoice_id else sale_order_id.partner_id.id,
            'partner_shipping_id': sale_order_id.partner_shipping_id.id,
            'fiscal_position_id': (
                    sale_order_id.fiscal_position_id or sale_order_id.fiscal_position_id.get_fiscal_position(
                sale_order_id.partner_invoice_id.id)).id,
            'partner_bank_id': sale_order_id.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': sale_order_id.name,
            'invoice_payment_term_id': sale_order_id.payment_term_id.id,
            'payment_reference': sale_order_id.reference,
            'transaction_ids': [(6, 0, sale_order_id.transaction_ids.ids)],
            "invoice_line_ids": invoice_lines,
            'company_id': sale_order_id.company_id.id,
            # 'operating_unit_id': self.operating_unit.id,
            'fromdate': self.fromdate,
            'todate': self.todate,

        }
        return invoice_vals

    def refund(self):
        invoice_lines = []
        invoice_lines.append([0, 0, self._prepare_refund_invoice_line()])
        vals = self._prepare_refund_invoices(self, invoice_lines)
        invoice = self.env['account.move'].create(vals)
        invoice.invoice_date = fields.Date.today()
        # invoice.action_review()
        invoice.action_post()
        # self.status = 'invoiced'
        self.refund_insurance = True
        return invoice

    @api.depends('state', 'order_line', 'order_line.product_uom_qty', 'order_line.qty_delivered',
                 'order_line.qty_returned')
    def _compute_rental_status(self):
        # TODO replace multiple assignations by one write?
        for order in self:
            if order.state in ['sale', 'done', 'occupied', 'termination'] and order.is_rental_order:
                rental_order_lines = order.order_line.filtered('is_rental')
                pickeable_lines = rental_order_lines.filtered(lambda sol: sol.qty_delivered < sol.product_uom_qty)
                returnable_lines = rental_order_lines.filtered(lambda sol: sol.qty_returned < sol.qty_delivered)
                min_pickup_date = min(pickeable_lines.mapped('pickup_date')) if pickeable_lines else 0
                min_return_date = min(returnable_lines.mapped('return_date')) if returnable_lines else 0
                if pickeable_lines and (not returnable_lines or min_pickup_date <= min_return_date):
                    order.rental_status = 'pickup'
                    order.next_action_date = min_pickup_date
                elif returnable_lines:
                    order.rental_status = 'return'
                    # ToDO: Abdulrhman: Why You do This ?
                    # ToDO: the next code is for Abdulrhman
                    order.rental_status = 'pickup'
                    order.next_action_date = min_return_date
                else:
                    if order.state != 'termination':
                        order.rental_status = 'returned'
                        for line in self.order_line:
                            line.product_id.unit_rented = False
                    if self.state == 'sale':
                        order.rental_status = 'sent'
                    if self.state == 'occupied':
                        for line in self.order_line:
                            line.product_id.unit_rented = True
                        order.rental_status = 'pickup'
                        order.next_action_date = False
                order.has_pickable_lines = bool(pickeable_lines)
                order.has_returnable_lines = bool(returnable_lines)
            else:
                order.has_pickable_lines = False
                order.has_returnable_lines = False
                order.rental_status = order.state if order.is_rental_order else False
                order.next_action_date = False

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for line in self.order_line:
            line.product_id.unit_rented = False
        return res

    def action_pickup(self):
        self.write({'state': 'occupied', 'rental_status': 'return'})

    def _compute_has_late_lines(self):
        for order in self:
            order.has_late_lines = False

    @api.depends('state', 'amount_total', 'order_contract_invoice', 'order_contract_invoice.status')
    def _get_invoice_status(self):

        for order in self:
            invoice_lines = order.order_contract_invoice.mapped('status')
            if order.amount_total <= 0:
                order.invoice_status = 'no'
            elif any(invoice_status == 'uninvoiced' for invoice_status in invoice_lines) or not invoice_lines:
                order.invoice_status = 'to invoice'
            elif all(invoice_status == 'invoiced' for invoice_status in invoice_lines):
                order.invoice_status = 'invoiced'

    dayofweek = {
        '0': _('الاثنين'),
        '1': _('الثلاثاء'),
        '2': _('الأربعاء'),
        '3': _('الخميس'),
        '4': _('الجمعة'),
        '5': _('السبت'),
        '6': _('ألأخد')
    }


class RentSaleInvoices(models.Model):
    _inherit = 'rent.sale.invoices'

    contract_number = fields.Char(related="sale_order_id.contract_number")

    def _prepare_invoice(self, invoice_lines):
        res = super(RentSaleInvoices, self)._prepare_invoice(invoice_lines)
        res.update({
            'invoice_date': self.fromdate,
            'l10n_sa_delivery_date': self.fromdate,
            'invoice_date_due': self.fromdate,
        })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('property_number', 'product_id', 'fromdate', 'todate')
    def _set_product_domain(self):
        product_ids = []
        for line in self:
            orders = self.env['sale.order.line'].sudo().search([
                ('order_id.state', '=', 'occupied'),
                ('fromdate', '<', line.todate)
            ])
            product_ids = orders.product_id.ids
        return {'domain': {'product_id': [('product_tmpl_id.property_id','=',self.property_number.id),('id', 'not in', product_ids)]}}

