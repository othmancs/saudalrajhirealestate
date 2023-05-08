# -*- coding: utf-8 -*-

import math
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api
from odoo import models, fields, _
from odoo.exceptions import UserError



class AccountJournal(models.Model):
    _inherit = "account.journal"


    code = fields.Char(string='Short Code', size=50, required=True, help="Shorter name used for display. The journal entries of this journal will also be named using this prefix by default.")

class AccountMove(models.Model):
    _inherit = "account.move"

    # state = fields.Selection(selection=[
    #     ('draft', 'Draft'),
    #     ('review', 'Reviewed'),
    #     ('posted', 'Posted'),
    #     ('cancel', 'Cancelled'),
    # ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    renting_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="sale_attachment_rel",
                                              string='Attachments', compute="get_sale_attachment")
    renting_id = fields.Many2one('sale.order', compute="get_renting_id")
    invoice_months = fields.Integer(compute="get_months")

    @api.depends('fromdate', 'todate')
    def get_months(self):
        for rec in self:
            months = 0
            print(rec.fromdate, "=========== ", rec.todate)
            if rec.fromdate and rec.todate:
                fromdate = rec.fromdate.replace(day=1)
                todateMonth = rec.todate.month
                todate = rec.todate.replace(day=28)
                # todate = rec.todate.replace(month=todateMonth+1, day=1)
                print(fromdate, "=========== ", todate)
                date1 = datetime.strptime(str(fromdate)[:10], '%Y-%m-%d')
                date2 = datetime.strptime(str(todate)[:10], '%Y-%m-%d')
                difference = relativedelta(date2, date1)
                months = difference.months + 12 * difference.years
                # if difference.days > 0:
                #     months += 1
                if difference.days > 0:
                    months += 1
            print("IIIIIIIIIIIIIIIIIIIIII ", months)
            rec.invoice_months = months

    @api.depends('invoice_origin')
    def get_renting_id(self):
        for rec in self:
            rent_id = self.env['sale.order'].sudo().search([('name', '=', rec.invoice_origin)],limit=1)
            rec.renting_id = rent_id.id if rent_id else False

    @api.depends('invoice_origin')
    def get_sale_attachment(self):
        for rec in self:
            rec.renting_attachment_ids = [(6, 0, [])]
            sale_id = self.env['sale.order'].sudo().search([('name', '=', rec.invoice_origin)])
            if sale_id:
                attachment_ids = self.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'sale.order'),
                    ('res_id', '=', sale_id.id),
                ])
                rec.renting_attachment_ids = [(6, 0, attachment_ids.ids)]

    def action_review(self):
        self.state = 'review'

    def _auto_create_asset(self):
        create_list = []
        invoice_list = []
        auto_validate = []
        last = 0
        for move in self:
            if not move.is_invoice():
                continue

            for move_line in move.line_ids.filtered(lambda line: not (move.move_type in (
                    'out_invoice', 'out_refund') and line.account_id.user_type_id.internal_group == 'asset')):
                if (
                        move_line.account_id
                        and (move_line.account_id.can_create_asset)
                        and move_line.account_id.create_asset != "no"
                        and not move.reversed_entry_id
                        and not (move_line.currency_id or move.currency_id).is_zero(move_line.price_total)
                        and not move_line.asset_ids
                        and not move_line.tax_line_id
                        and move_line.price_total > 0
                ):
                    if not move_line.name:
                        raise UserError(
                            _('Journal Items of {account} should have a label in order to generate an asset').format(
                                account=move_line.account_id.display_name))
                    if move_line.account_id.multiple_assets_per_line:
                        # decimal quantities are not supported, quantities are rounded to the lower int
                        units_quantity = max(1, int(move_line.quantity))
                    else:
                        units_quantity = 1
                    vals = {
                        'name': move_line.name,
                        'company_id': move_line.company_id.id,
                        'currency_id': move_line.company_currency_id.id,
                        'account_analytic_id': move_line.analytic_account_id.id,
                        'analytic_tag_ids': [(6, False, move_line.analytic_tag_ids.ids)],
                        'original_move_line_ids': [(6, False, move_line.ids)],
                        'state': 'draft',
                    }
                    model_id = move_line.account_id.asset_model
                    fromdate = self.fromdate.replace(day=1)
                    todateMonth = self.todate.month
                    # todate = self.todate.replace(month=todateMonth + 1, day=1)
                    todate = self.todate.replace(day=28)
                    date1 = datetime.strptime(str(fromdate)[:10], '%Y-%m-%d')
                    date2 = datetime.strptime(str(todate)[:10], '%Y-%m-%d')
                    difference = relativedelta(date2, date1)
                    months = difference.months + 12 * difference.years
                    # if difference.days > 0:
                    #     months += 1


                    # date1 = datetime.strptime(str(self.rent_sale_line_id.sale_order_id.fromdate)[:10], '%Y-%m-%d')
                    # date2 = datetime.strptime(str(self.rent_sale_line_id.sale_order_id.todate)[:10], '%Y-%m-%d')
                    # difference = relativedelta(date2, date1)
                    # months = difference.months + 12 * difference.years
                    # if difference.days > 0:
                    #     months += 1
                    # last = model_id.method_number
                    # model_id.method_number = months / self.rent_sale_line_id.sale_order_id.invoice_number

                    if model_id:
                        vals.update({
                            'model_id': model_id.id,
                        })
                    auto_validate.extend([move_line.account_id.create_asset == 'validate'] * units_quantity)
                    invoice_list.extend([move] * units_quantity)
                    for i in range(1, units_quantity + 1):
                        if units_quantity > 1:
                            vals['name'] = move_line.name + _(" (%s of %s)", i, units_quantity)
                        create_list.extend([vals.copy()])

        assets = self.env['account.asset'].create(create_list)
        for asset, vals, invoice, validate in zip(assets, create_list, invoice_list, auto_validate):
            if 'model_id' in vals:
                asset.prorata = True
                asset.prorata_date = asset.acquisition_date

                asset._onchange_model_id()
                if validate:
                    asset.validate()
            if invoice:
                asset_name = {
                    'purchase': _('Asset'),
                    'sale': _('Deferred revenue'),
                    'expense': _('Deferred expense'),
                }[asset.asset_type]
                msg = _('%s created from invoice') % (asset_name)
                msg += ': <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>' % (invoice.id, invoice.name)
                asset.message_post(body=msg)
                # Abdulrhman Change
                asset.set_to_draft()
                asset.model_id.method_number = math.floor(months)
                asset.method_number = math.floor(months)
                asset.prorata = True
                asset.prorata_date = invoice.fromdate or invoice.invoice_date
                asset.acquisition_date = invoice.fromdate or invoice.invoice_date
                asset.compute_depreciation_board()
                # asset.validate()

        # assets.validate()
        # if last > 0:
        #     asset.model_id.method_number = last

        return assets

    temp_sale_order_id = fields.Many2one('sale.order', string="Temp sale order")

    def get_temp_sale_order_id(self):
        for rec in self:
            for line in self.env['account.move'].search([('move_type', '=', 'out_invoice')]):
                temp_sale_order_id = self.env['sale.order'].search([('name', '=', line.invoice_origin)])
                if not line.temp_sale_order_id:
                    line.temp_sale_order_id = temp_sale_order_id.id

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            for line in rec.asset_ids:
                if line.depreciation_move_ids:
                    for dep in line.depreciation_move_ids.sorted(reverse=False):
                        dep.button_draft()
                        dep.unlink()
                line.set_to_running()
                line.set_to_draft()
                date1 = datetime.strptime(str(rec.fromdate)[:10], '%Y-%m-%d')
                date2 = datetime.strptime(str(rec.todate)[:10], '%Y-%m-%d')
                difference = relativedelta(date2, date1)
                months = difference.months + 12 * difference.years
                # if difference.days > 0:
                #     months += 1
                print(rec.fromdate, "XXXXXXXXXXXXXXXXXmionnnnnnnXXXXXXXXxXx", rec.todate)
                print(months)
                line.model_id.method_number = math.floor(months)
                line.method_number = math.floor(months)
                line.prorata = True
                line.prorata_date = line.acquisition_date
                line.acquisition_date = self.fromdate or self.invoice_date
                line.prorata_date = self.fromdate or self.invoice_date
                line.compute_depreciation_board()
                # line.validate()

                # if rec.rent_sale_line_id:
                #     for dep in line.depreciation_move_ids.sorted(reverse=False):
                #         dep.button_draft()
                #         dep.unlink()
                #     line.set_to_running()
                #     line.set_to_draft()
                #     date1 = datetime.strptime(str(rec.rent_sale_line_id.sale_order_id.fromdate)[:10], '%Y-%m-%d')
                #     date2 = datetime.strptime(str(rec.rent_sale_line_id.sale_order_id.todate)[:10], '%Y-%m-%d')
                #     difference = relativedelta(date2, date1)
                #     months = difference.months + 12 * difference.years
                #     if difference.days > 0:
                #         months += 1
                #     line.model_id.method_number = math.floor(
                #         months / rec.rent_sale_line_id.sale_order_id.invoice_number)
                #     line.method_number = math.floor(months / rec.rent_sale_line_id.sale_order_id.invoice_number)
                #     line.prorata = True
                #     line.prorata_date = line.acquisition_date
                #     line.prorata_date = self.fromdate or self.invoice_date
                #     line.compute_depreciation_board()
                #     line.validate()
                #
                # else:
                #     for dep in line.depreciation_move_ids:
                #         dep.button_draft()
                #         dep.unlink()
                #     line.set_to_running()
                #     line.set_to_draft()
                #     date1 = datetime.strptime(str(rec.temp_sale_order_id.fromdate)[:10], '%Y-%m-%d')
                #     date2 = datetime.strptime(str(rec.temp_sale_order_id.todate)[:10], '%Y-%m-%d')
                #     difference = relativedelta(date2, date1)
                #     months = difference.months + 12 * difference.years
                #     if difference.days > 0:
                #         months += 1
                #     line.model_id.method_number = math.floor(months / rec.temp_sale_order_id.invoice_number)
                #     line.method_number = math.floor(months / rec.temp_sale_order_id.invoice_number)
                #     line.prorata_date = line.acquisition_date
                #     line.prorata_date = self.fromdate or self.invoice_date
                #     line.compute_depreciation_board()
                #     line.validate()

        return res



    def fix_defe(self):

        invoice_ids = self
        for rec in invoice_ids:
            for ddd in rec.asset_ids:
                ddd.unlink_lines()
                ddd.unlink()
        for invoice in invoice_ids:
            invoice._auto_create_asset()
            invoice.env.cr.commit()
            for line in invoice.asset_ids:
                line.unlink_lines()
                line.set_to_running()
                line.set_to_draft()
                fromdate = invoice.fromdate.replace(day=1)
                todateMonth = invoice.todate.month
                # todate = invoice.todate.replace(month=todateMonth + 1, day=1)
                todate = invoice.todate.replace(day=28)
                date1 = datetime.strptime(str(fromdate)[:10], '%Y-%m-%d')
                date2 = datetime.strptime(str(todate)[:10], '%Y-%m-%d')
                difference = relativedelta(date2, date1)
                months = difference.months + 12 * difference.years
                if difference.days >0:
                    months +=1
                line.model_id.method_number = math.floor(months)
                line.method_number = math.floor(months)
                line.prorata = True
                line.prorata_date = line.acquisition_date
                line.prorata_date = invoice.fromdate or invoice.invoice_date
                line.acquisition_date = invoice.fromdate or invoice.invoice_date
                line.compute_depreciation_board()
                line.validate()


    def fix_deferreds(self):
            # deferreds = self.env["account.asset"].search(
            #     [("state", "!=", "model"), ("asset_type", "=", "sale")]
            # )
            invoice_ids = self.env['account.move'].search([('temp_sale_order_id', '!=', False)])
            for invoice  in invoice_ids:
                print(invoice.asset_remaining_value, "Invoiceeeeee", invoice)
                if invoice.state == 'posted':
                    print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww", invoice)
                    invoice.fix_defe()


# def fix_deferreds():
#     deferreds = self.env["account.asset"].search([
#         ('asset_type', '=', 'sale'),
#         ('state', 'not in', ['model', 'open', 'close']),
#         ('parent_id', '=', False),
#         ("id", "not in", [4077, 4079])]
#     )
#     for line in deferreds:
#         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", line)
#         line.validate()
#         line.env.cr.commit()



